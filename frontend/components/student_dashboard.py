
import streamlit as st
import requests

API_URL = "http://localhost:8000"

def student_dashboard():

    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"👨‍🎓 Welcome, {st.session_state.full_name}!")
    with col2:
        if st.button("🚪 Sign Out", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()
    
    st.markdown("---")
    
    # Get subjects
    try:
        response = requests.get(f"{API_URL}/student/subjects")
        subjects = response.json().get("subjects", [])
    except:
        subjects = []
    
    if not subjects:
        st.info("📚 No study materials available yet. Please contact your faculty to upload materials.")
        return
    
    # Subject and Unit selection
    col1, col2 = st.columns(2)
    with col1:
        subject = st.selectbox("📖 Select Subject", subjects, key="student_subject")
    
    # Get units for selected subject
    if subject:
        try:
            response = requests.get(f"{API_URL}/student/units/{subject}")
            units = response.json().get("units", [])
        except:
            units = []
        
        with col2:
            unit = st.selectbox("📑 Select Unit", units if units else ["No units available"], key="student_unit")
    else:
        unit = None
    
    if not subject or not unit or unit == "No units available":
        st.warning("Please select a subject and unit to continue")
        return
    
    st.markdown("---")
    
    # Feature tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📘 Summarize", "❓ MCQ Practice", "🧠 Flashcards", "💬 Ask Question"])
    
    # Tab 1: Summarize
    with tab1:
        st.subheader("📘 Chapter Summary")
        st.write("Get AI-generated structured notes from your study materials")
        
        if st.button("Generate Summary", key="gen_summary", use_container_width=True):
            with st.spinner("Generating summary..."):
                try:
                    response = requests.post(
                        f"{API_URL}/student/summary",
                        json={"subject": subject, "unit": unit}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data["status"] == "success":
                            st.success("✅ Summary generated!")
                            st.markdown(data["summary"])
                        else:
                            st.error(data.get("message", "Failed to generate summary"))
                    else:
                        st.error(response.json().get("detail", "Error generating summary"))
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Tab 2: MCQ Practice
    with tab2:
        st.subheader("❓ Multiple Choice Questions")
        st.write("Test your knowledge with AI-generated MCQs")
        
        # Initialize session state for MCQ quiz
        if "quiz_active" not in st.session_state:
            st.session_state.quiz_active = False
        if "quiz_questions" not in st.session_state:
            st.session_state.quiz_questions = []
        if "quiz_current" not in st.session_state:
            st.session_state.quiz_current = 0
        if "quiz_total" not in st.session_state:
            st.session_state.quiz_total = 10
        if "quiz_answers" not in st.session_state:
            st.session_state.quiz_answers = {}  # {question_num: {'selected': 'A', 'correct': 'B', 'attempts': 2}}
        if "answer_checked" not in st.session_state:
            st.session_state.answer_checked = False
        if "selected_option" not in st.session_state:
            st.session_state.selected_option = None
        
        # Start Quiz Section
        if not st.session_state.quiz_active:
            col1, col2 = st.columns([3, 1])
            with col2:
                num_questions = st.number_input("Number of Questions", min_value=5, max_value=20, value=10, key="num_mcqs")
            
            if st.button("Start Quiz", key="gen_mcq", use_container_width=True):
                st.session_state.quiz_active = True
                st.session_state.quiz_total = num_questions
                st.session_state.quiz_current = 1
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = {}
                st.session_state.answer_checked = False
                st.session_state.selected_option = None
                st.experimental_rerun()
        
        # Active Quiz Section
        else:
            current_q_num = st.session_state.quiz_current
            total_q = st.session_state.quiz_total
            
            # Quiz hasn't finished
            if current_q_num <= total_q:
                # Display progress
                st.markdown(f"### Question {current_q_num} of {total_q}")
                st.progress(current_q_num / total_q)
                
                # Generate current question if not already in the list
                if len(st.session_state.quiz_questions) < current_q_num:
                    with st.spinner(f"Generating question {current_q_num}..."):
                        try:
                            # Build context of previously asked questions
                            previous_questions = []
                            for prev_q in st.session_state.quiz_questions:
                                previous_questions.append(prev_q['question'])
                            
                            # Prepare request payload
                            request_data = {
                                "subject": subject,
                                "unit": unit,
                                "count": 1
                            }
                            
                            # Add previous questions to avoid repetition
                            if previous_questions:
                                request_data["previous_questions"] = previous_questions
                            
                            response = requests.post(
                                f"{API_URL}/student/mcq",
                                json=request_data
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                if data["status"] == "success" and len(data["mcqs"]) > 0:
                                    st.session_state.quiz_questions.append(data["mcqs"][0])
                                    # Initialize answer tracking for this question
                                    if current_q_num not in st.session_state.quiz_answers:
                                        st.session_state.quiz_answers[current_q_num] = {
                                            'attempts': 0,
                                            'correct': False,
                                            'selected': None
                                        }
                                    st.experimental_rerun()
                                else:
                                    st.error(data.get("message", "Failed to generate question"))
                            else:
                                st.error(response.json().get("detail", "Error generating question"))
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                # Display current question
                if len(st.session_state.quiz_questions) >= current_q_num:
                    mcq = st.session_state.quiz_questions[current_q_num - 1]
                    
                    # Question card
                    st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 30px;
                        border-radius: 15px;
                        color: white;
                        margin-bottom: 20px;
                        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                    '>
                        <h4 style='margin: 0; font-size: 20px;'>{mcq['question']}</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    options = mcq["options"]
                    correct_answer = mcq["correct_answer"]
                    
                    # Display options
                    if not st.session_state.answer_checked:
                        # Create a unique key for this specific question
                        selected = st.radio(
                            "Select your answer:",
                            list(options.keys()),
                            format_func=lambda x: f"{x}) {options[x]}",
                            key=f"mcq_option_{current_q_num}"
                        )
                        
                        if st.button("Submit Answer", key=f"submit_{current_q_num}", disabled=selected is None, use_container_width=True):
                            st.session_state.answer_checked = True
                            st.session_state.selected_option = selected
                            st.session_state.quiz_answers[current_q_num]['attempts'] += 1
                            st.session_state.quiz_answers[current_q_num]['selected'] = selected
                            st.experimental_rerun()
                    
                    # Show result after checking
                    else:
                        selected = st.session_state.selected_option
                        attempts = st.session_state.quiz_answers[current_q_num]['attempts']
                        
                        # Display options with enhanced visuals
                        st.markdown("### Answer Options:")
                        
                        for key in options.keys():
                            option_text = options[key]
                            
                            if key == selected and key == correct_answer:
                                # User selected correct answer - Green
                                st.markdown(f"""
                                <div style='
                                    background-color: #d4edda;
                                    border-left: 5px solid #28a745;
                                    padding: 15px;
                                    margin: 10px 0;
                                    border-radius: 5px;
                                    color: #155724;
                                '>
                                    <strong>✅ {key}) {option_text}</strong>
                                    <br><span style='font-size: 12px;'>✓ Your Answer (Correct!)</span>
                                </div>
                                """, unsafe_allow_html=True)
                                
                            elif key == selected and key != correct_answer:
                                # User selected wrong answer - Red
                                st.markdown(f"""
                                <div style='
                                    background-color: #f8d7da;
                                    border-left: 5px solid #dc3545;
                                    padding: 15px;
                                    margin: 10px 0;
                                    border-radius: 5px;
                                    color: #721c24;
                                '>
                                    <strong>❌ {key}) {option_text}</strong>
                                    <br><span style='font-size: 12px;'>✘ Your Answer (Incorrect)</span>
                                </div>
                                """, unsafe_allow_html=True)
                                
                            elif key == correct_answer:
                                # Correct answer not selected - Green with indicator
                                st.markdown(f"""
                                <div style='
                                    background-color: #d1ecf1;
                                    border-left: 5px solid #17a2b8;
                                    padding: 15px;
                                    margin: 10px 0;
                                    border-radius: 5px;
                                    color: #0c5460;
                                '>
                                    <strong>✅ {key}) {option_text}</strong>
                                    <br><span style='font-size: 12px;'>✓ Correct Answer</span>
                                </div>
                                """, unsafe_allow_html=True)
                                
                            else:
                                # Other options - Gray
                                st.markdown(f"""
                                <div style='
                                    background-color: #f8f9fa;
                                    border-left: 5px solid #6c757d;
                                    padding: 15px;
                                    margin: 10px 0;
                                    border-radius: 5px;
                                    color: #495057;
                                '>
                                    {key}) {option_text}
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Show explanation
                        st.info(f"💡 **Explanation:** {mcq['explanation']}")
                        
                        # Action buttons
                        if selected == correct_answer:
                            # Correct answer - mark as correct
                            st.session_state.quiz_answers[current_q_num]['correct'] = True
                            st.success(f"🎉 Correct! (Attempts: {attempts})")
                            
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                if st.button("Next Question ➡️", key=f"next_{current_q_num}", use_container_width=True):
                                    # Move to next question
                                    st.session_state.quiz_current += 1
                                    st.session_state.answer_checked = False
                                    st.session_state.selected_option = None
                                    st.experimental_rerun()
                        else:
                            # Wrong answer - offer reattempt or next
                            st.warning(f"⚠️ Incorrect. Attempts so far: {attempts}")
                            
                            col1, col2, col3 = st.columns([1, 1, 2])
                            with col1:
                                if st.button("🔄 Reattempt", key=f"reattempt_{current_q_num}", use_container_width=True):
                                    st.session_state.answer_checked = False
                                    st.session_state.selected_option = None
                                    st.experimental_rerun()
                            
                            with col2:
                                if st.button("Next Question ➡️", key=f"skip_{current_q_num}", use_container_width=True):
                                    # Move to next question without marking correct
                                    st.session_state.quiz_current += 1
                                    st.session_state.answer_checked = False
                                    st.session_state.selected_option = None
                                    st.experimental_rerun()
            
            # Quiz finished - show summary
            else:
                st.markdown("## 🎉 Quiz Complete!")
                st.balloons()
                
                # Calculate statistics
                correct_count = sum(1 for ans in st.session_state.quiz_answers.values() if ans['correct'])
                total_attempts = sum(ans['attempts'] for ans in st.session_state.quiz_answers.values())
                score_percentage = (correct_count / total_q) * 100
                
                # Display score
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Score", f"{correct_count}/{total_q}")
                with col2:
                    st.metric("Percentage", f"{score_percentage:.1f}%")
                with col3:
                    st.metric("Total Attempts", total_attempts)
                
                # Performance message
                if score_percentage >= 80:
                    st.success("🌟 Excellent performance!")
                elif score_percentage >= 60:
                    st.info("👍 Good job! Keep practicing.")
                else:
                    st.warning("📚 Keep studying and try again!")
                
                st.markdown("---")
                st.markdown("### 📋 Question Review")
                
                # Display all questions with answers
                for i, mcq in enumerate(st.session_state.quiz_questions, 1):
                    ans_data = st.session_state.quiz_answers.get(i, {})
                    selected = ans_data.get('selected', 'Not answered')
                    attempts = ans_data.get('attempts', 0)
                    is_correct = ans_data.get('correct', False)
                    
                    with st.expander(f"{'✅' if is_correct else '❌'} Question {i} - {mcq['question'][:60]}... (Attempts: {attempts})"):
                        st.markdown(f"**Question:** {mcq['question']}")
                        st.markdown("")
                        st.markdown("**Options:**")
                        for key, value in mcq['options'].items():
                            if key == selected and key == mcq['correct_answer']:
                                st.success(f"✅ {key}) {value} (Your answer - Correct!)")
                            elif key == selected:
                                st.error(f"❌ {key}) {value} (Your answer)")
                            elif key == mcq['correct_answer']:
                                st.success(f"✅ {key}) {value} (Correct answer)")
                            else:
                                st.write(f"{key}) {value}")
                        st.info(f"💡 **Explanation:** {mcq['explanation']}")
                
                # Restart quiz button
                st.markdown("---")
                if st.button("Start New Quiz", key="restart_quiz", use_container_width=True):
                    st.session_state.quiz_active = False
                    st.session_state.quiz_questions = []
                    st.session_state.quiz_current = 0
                    st.session_state.quiz_answers = {}
                    st.session_state.answer_checked = False
                    st.session_state.selected_option = None
                    st.experimental_rerun()
    
    # Tab 3: Flashcards
    with tab3:
        st.subheader("🧠 Flashcards")
        st.write("Quick revision cards covering the entire unit")
        
        # Initialize session state for flashcard session
        if "flashcard_active" not in st.session_state:
            st.session_state.flashcard_active = False
        if "flashcard_list" not in st.session_state:
            st.session_state.flashcard_list = []
        if "flashcard_current" not in st.session_state:
            st.session_state.flashcard_current = 0
        if "flashcard_total" not in st.session_state:
            st.session_state.flashcard_total = 10
        
        # Start Flashcard Session
        if not st.session_state.flashcard_active:
            col1, col2 = st.columns([3, 1])
            with col2:
                num_cards = st.number_input("Number of Cards", min_value=5, max_value=20, value=10, key="num_cards")
            
            if st.button("Start Flashcards", key="gen_flashcards", use_container_width=True):
                st.session_state.flashcard_active = True
                st.session_state.flashcard_total = num_cards
                st.session_state.flashcard_current = 1
                st.session_state.flashcard_list = []
                st.experimental_rerun()
        
        # Active Flashcard Session
        else:
            current_card_num = st.session_state.flashcard_current
            total_cards = st.session_state.flashcard_total
            
            # Session not finished
            if current_card_num <= total_cards:
                # Display progress
                st.markdown(f"### Card {current_card_num} of {total_cards}")
                st.progress(current_card_num / total_cards)
                
                # Generate current flashcard if not already in the list
                if len(st.session_state.flashcard_list) < current_card_num:
                    with st.spinner(f"Generating flashcard {current_card_num}..."):
                        try:
                            # Build context of previously generated flashcards
                            previous_cards = []
                            for prev_card in st.session_state.flashcard_list:
                                previous_cards.append(prev_card['front'])
                            
                            # Prepare request payload
                            request_data = {
                                "subject": subject,
                                "unit": unit,
                                "count": 1
                            }
                            
                            # Add previous flashcards to avoid repetition
                            if previous_cards:
                                request_data["previous_cards"] = previous_cards
                            
                            response = requests.post(
                                f"{API_URL}/student/flashcards",
                                json=request_data
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                if data["status"] == "success" and len(data["flashcards"]) > 0:
                                    st.session_state.flashcard_list.append(data["flashcards"][0])
                                    st.experimental_rerun()
                                else:
                                    st.error(data.get("message", "Failed to generate flashcard"))
                            else:
                                st.error(response.json().get("detail", "Error generating flashcard"))
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                # Display current flashcard
                if len(st.session_state.flashcard_list) >= current_card_num:
                    card = st.session_state.flashcard_list[current_card_num - 1]
                    
                    # Create unique flip state for this card number
                    flip_key = f"card_flipped_{current_card_num}"
                    if flip_key not in st.session_state:
                        st.session_state[flip_key] = False
                    
                    # Card display variables
                    card_color = "#667eea" if not st.session_state[flip_key] else "#764ba2"
                    card_label = "Question" if not st.session_state[flip_key] else "Answer"
                    card_content = card['front'] if not st.session_state[flip_key] else card['back']
                    
                    with st.container():
                        st.markdown(f"""
                        <div style='
                            background: linear-gradient(135deg, {card_color} 0%, #764ba2 100%);
                            padding: 50px 30px;
                            border-radius: 15px;
                            text-align: center;
                            color: white;
                            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
                            min-height: 200px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                        '>
                            <h4 style='margin-bottom: 20px; opacity: 0.9;'>{card_label}</h4>
                            <p style='font-size: 20px; line-height: 1.6; margin: 0;'>
                                {card_content}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("")
                    col1, col2, col3 = st.columns([1, 1, 2])
                    
                    with col1:
                        if st.button("🔄 Flip Card", key=f"flip_{current_card_num}", use_container_width=True):
                            st.session_state[flip_key] = not st.session_state[flip_key]
                            st.experimental_rerun()
                    
                    with col2:
                        if st.button("Next Card ➡️", key=f"next_card_{current_card_num}", use_container_width=True):
                            # Move to next card
                            st.session_state.flashcard_current += 1
                            st.experimental_rerun()
            
            # Session finished - show summary
            else:
                st.markdown("## 🎉 Flashcard Review Complete!")
                st.balloons()
                
                st.success(f"✅ You've reviewed all {total_cards} flashcards covering the entire unit!")
                
                st.markdown("---")
                st.markdown("### 📚 All Flashcards")
                
                # Display all flashcards
                for i, card in enumerate(st.session_state.flashcard_list, 1):
                    with st.expander(f"📎 Flashcard {i} - {card['front'][:50]}..."):
                        st.markdown(f"**Front (Question):**")
                        st.info(card['front'])
                        st.markdown(f"**Back (Answer):**")
                        st.success(card['back'])
                
                # Restart button
                st.markdown("---")
                if st.button("Start New Review", key="restart_flashcards", use_container_width=True):
                    st.session_state.flashcard_active = False
                    st.session_state.flashcard_list = []
                    st.session_state.flashcard_current = 0
                    # Clear all flip states
                    for key in list(st.session_state.keys()):
                        if key.startswith('card_flipped_'):
                            del st.session_state[key]
                    st.experimental_rerun()
    
    # Tab 4: Ask Question
    with tab4:
        st.subheader("💬 Ask a Question")
        st.write("Get answers from your study materials using AI")
        
        question = st.text_area("Enter your question:", key="student_question", height=100)
        
        if st.button("Get Answer", key="ask_question", use_container_width=True):
            if not question:
                st.warning("Please enter a question")
            else:
                with st.spinner("Finding answer..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/student/ask",
                            json={"subject": subject, "unit": unit, "question": question}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data["status"] == "success":
                                st.success("✅ Answer found!")
                                st.markdown("### Answer:")
                                st.write(data["answer"])
                                st.caption(f"📚 Sources: {', '.join(data.get('sources', []))}")
                            else:
                                st.error(data.get("message", "Failed to get answer"))
                        else:
                            st.error(response.json().get("detail", "Error getting answer"))
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
