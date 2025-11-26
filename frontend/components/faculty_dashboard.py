
import streamlit as st
import requests
import os

API_URL = "http://localhost:8000"

def faculty_dashboard():

    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"👩‍🏫 Faculty Dashboard - {st.session_state.full_name}")
    with col2:
        if st.button("🚪 Sign Out", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()
    
    st.markdown("---")
    
    # Tabs for different functions
    tab1, tab2 = st.tabs(["📤 Upload Materials", "📊 Preview Content"])
    
    # Tab 1: Upload Materials
    with tab1:
        st.subheader("📤 Upload Study Materials")
        
        # Get existing subjects for dropdown or new input
        try:
            response = requests.get(f"{API_URL}/faculty/subjects")
            existing_subjects = response.json().get("subjects", [])
        except:
            existing_subjects = []
        
        col1, col2 = st.columns(2)
        with col1:
            # Option to select existing subject or create new
            use_existing = st.checkbox("📂 Use existing subject", key="use_existing_subject")
            
            if use_existing and existing_subjects:
                subject = st.selectbox("Select Subject", existing_subjects, key="upload_subject_select")
            else:
                subject = st.text_input("Subject Name", key="upload_subject", placeholder="e.g., Physics, Edge AI")
        
        with col2:
            # If subject is selected, show existing units
            if subject and use_existing:
                try:
                    response = requests.get(f"{API_URL}/faculty/units/{subject}")
                    existing_units = response.json().get("units", [])
                except:
                    existing_units = []
                
                use_existing_unit = st.checkbox("📁 Use existing unit (will replace files)", key="use_existing_unit")
                
                if use_existing_unit and existing_units:
                    unit = st.selectbox("Select Unit", existing_units, key="upload_unit_select")
                    st.warning("⚠️ Warning: Uploading to existing unit will REPLACE all current files!")
                else:
                    unit = st.text_input("New Unit Name", key="upload_unit", placeholder="e.g., Unit 1, Chapter 2")
            else:
                unit = st.text_input("Unit Name", key="upload_unit", placeholder="e.g., Unit 1, Chapter 2")
        
        uploaded_file = st.file_uploader(
            "Choose a file (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            key="file_upload"
        )
        
        if st.button("Upload File", key="upload_btn", use_container_width=True):
            if not subject or not unit:
                st.error("Please provide both subject and unit names")
            elif not uploaded_file:
                st.error("Please select a file to upload")
            else:
                with st.spinner("Uploading file..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        
                        # Check if replacing existing unit
                        replace_mode = use_existing and subject in existing_subjects and 'use_existing_unit' in st.session_state and st.session_state.use_existing_unit
                        
                        data = {
                            "subject": subject,
                            "unit": unit,
                            "replace": "true" if replace_mode else "false"
                        }
                        
                        response = requests.post(
                            f"{API_URL}/faculty/upload",
                            files=files,
                            data=data
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            if replace_mode:
                                st.success(f"✅ File '{result['filename']}' uploaded! Previous files in {subject}/{unit} have been replaced.")
                            else:
                                st.success(f"✅ File '{result['filename']}' uploaded successfully!")
                            st.info("🤖 Embeddings are being generated automatically in the background. This may take a few minutes.")
                            st.info("📄 Students will be able to access AI features once processing is complete.")
                        else:
                            st.error(response.json().get("detail", "Upload failed"))
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        st.markdown("---")
        st.caption("📋 Supported formats: PDF, DOCX, TXT")
        st.caption("⚙️ Embeddings are generated automatically in the background")
        st.caption("🔄 Uploading to existing unit replaces all previous files")

    # Tab 2: Preview Content
    with tab2:
        st.subheader("📊 Preview Generated Content")
        st.write("Review AI-generated summaries, MCQs, and flashcards")
        
        # Get subjects
        try:
            response = requests.get(f"{API_URL}/faculty/subjects")
            subjects = response.json().get("subjects", [])
        except:
            subjects = []
        
        if not subjects:
            st.info("No subjects found. Please upload materials first.")
        else:
            # Subject and Unit selection
            col1, col2 = st.columns(2)
            with col1:
                subject = st.selectbox("Select Subject", subjects, key="select_preview_subject")
            
            # Get units
            if subject:
                try:
                    response = requests.get(f"{API_URL}/faculty/units/{subject}")
                    units = response.json().get("units", [])
                except:
                    units = []
                
                with col2:
                    unit = st.selectbox("Select Unit", units if units else ["No units"], key="select_preview_unit")
            
            if subject and unit and unit != "No units":
                st.markdown("---")
                
                # Initialize session state for preview
                if "preview_mcqs" not in st.session_state:
                    st.session_state.preview_mcqs = []
                if "preview_flashcards" not in st.session_state:
                    st.session_state.preview_flashcards = []
                if "preview_generating" not in st.session_state:
                    st.session_state.preview_generating = False
                if "preview_gen_type" not in st.session_state:
                    st.session_state.preview_gen_type = None
                if "preview_gen_count" not in st.session_state:
                    st.session_state.preview_gen_count = 0
                if "preview_gen_total" not in st.session_state:
                    st.session_state.preview_gen_total = 10
                
                # Tabs for different content types
                preview_tabs = st.tabs(["📝 Summary", "❓ MCQs", "🧠 Flashcards"])
                
                # Tab: Summary
                with preview_tabs[0]:
                    st.markdown("### Generate Summary")
                    if st.button("📝 Generate Summary", use_container_width=True, key="gen_summary_btn"):
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
                                    st.error(response.json().get("detail", "Error"))
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                
                # Tab: MCQs
                with preview_tabs[1]:
                    st.markdown("### Generate MCQs")
                    
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        num_mcqs = st.number_input("Number of MCQs", min_value=1, max_value=20, value=10, key="faculty_num_mcqs")
                    
                    with col1:
                        if st.button("❓ Generate MCQs", use_container_width=True, key="gen_mcqs_btn"):
                            st.session_state.preview_mcqs = []
                            st.session_state.preview_generating = True
                            st.session_state.preview_gen_type = "mcq"
                            st.session_state.preview_gen_count = 0
                            st.session_state.preview_gen_total = num_mcqs
                            st.experimental_rerun()
                    
                    # Generate MCQs one by one
                    if st.session_state.preview_generating and st.session_state.preview_gen_type == "mcq":
                        current = st.session_state.preview_gen_count
                        total = st.session_state.preview_gen_total
                        
                        if current < total:
                            # Generate next MCQ
                            with st.spinner(f"Generating MCQ {current + 1} of {total}..."):
                                st.progress((current + 1) / total)
                                try:
                                    # Build previous questions
                                    previous_questions = [q['question'] for q in st.session_state.preview_mcqs]
                                    
                                    request_data = {
                                        "subject": subject,
                                        "unit": unit,
                                        "count": 1
                                    }
                                    if previous_questions:
                                        request_data["previous_questions"] = previous_questions
                                    
                                    response = requests.post(
                                        f"{API_URL}/student/mcq",
                                        json=request_data
                                    )
                                    
                                    if response.status_code == 200:
                                        data = response.json()
                                        if data["status"] == "success" and len(data["mcqs"]) > 0:
                                            st.session_state.preview_mcqs.append(data["mcqs"][0])
                                            st.session_state.preview_gen_count += 1
                                            st.experimental_rerun()
                                        else:
                                            st.error(data.get("message", "Failed to generate MCQ"))
                                            st.session_state.preview_generating = False
                                    else:
                                        st.error(response.json().get("detail", "Error"))
                                        st.session_state.preview_generating = False
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                                    st.session_state.preview_generating = False
                        else:
                            # Generation complete
                            st.session_state.preview_generating = False
                            st.experimental_rerun()
                    
                    # Display all generated MCQs
                    if len(st.session_state.preview_mcqs) > 0:
                        st.markdown("---")
                        st.success(f"✅ Generated {len(st.session_state.preview_mcqs)} MCQs")
                        st.markdown("### All MCQs")
                        
                        for i, mcq in enumerate(st.session_state.preview_mcqs, 1):
                            with st.expander(f"❓ Question {i}", expanded=False):
                                st.markdown(f"**Question {i}:**")
                                st.write(mcq['question'])
                                st.markdown("")
                                st.markdown("**Options:**")
                                for key, value in mcq['options'].items():
                                    st.write(f"{key}) {value}")
                                st.markdown("")
                                st.markdown(f"**Correct Answer:** {mcq['correct_answer']}")
                                st.markdown(f"**Explanation:** {mcq['explanation']}")
                
                # Tab: Flashcards
                with preview_tabs[2]:
                    st.markdown("### Generate Flashcards")
                    
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        num_cards = st.number_input("Number of Cards", min_value=1, max_value=20, value=10, key="faculty_num_cards")
                    
                    with col1:
                        if st.button("🧠 Generate Flashcards", use_container_width=True, key="gen_cards_btn"):
                            st.session_state.preview_flashcards = []
                            st.session_state.preview_generating = True
                            st.session_state.preview_gen_type = "flashcard"
                            st.session_state.preview_gen_count = 0
                            st.session_state.preview_gen_total = num_cards
                            st.experimental_rerun()
                    
                    # Generate Flashcards one by one
                    if st.session_state.preview_generating and st.session_state.preview_gen_type == "flashcard":
                        current = st.session_state.preview_gen_count
                        total = st.session_state.preview_gen_total
                        
                        if current < total:
                            # Generate next flashcard
                            with st.spinner(f"Generating Flashcard {current + 1} of {total}..."):
                                st.progress((current + 1) / total)
                                try:
                                    # Build previous cards
                                    previous_cards = [c['front'] for c in st.session_state.preview_flashcards]
                                    
                                    request_data = {
                                        "subject": subject,
                                        "unit": unit,
                                        "count": 1
                                    }
                                    if previous_cards:
                                        request_data["previous_cards"] = previous_cards
                                    
                                    response = requests.post(
                                        f"{API_URL}/student/flashcards",
                                        json=request_data
                                    )
                                    
                                    if response.status_code == 200:
                                        data = response.json()
                                        if data["status"] == "success" and len(data["flashcards"]) > 0:
                                            st.session_state.preview_flashcards.append(data["flashcards"][0])
                                            st.session_state.preview_gen_count += 1
                                            st.experimental_rerun()
                                        else:
                                            st.error(data.get("message", "Failed to generate flashcard"))
                                            st.session_state.preview_generating = False
                                    else:
                                        st.error(response.json().get("detail", "Error"))
                                        st.session_state.preview_generating = False
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                                    st.session_state.preview_generating = False
                        else:
                            # Generation complete
                            st.session_state.preview_generating = False
                            st.experimental_rerun()
                    
                    # Display all generated flashcards
                    if len(st.session_state.preview_flashcards) > 0:
                        st.markdown("---")
                        st.success(f"✅ Generated {len(st.session_state.preview_flashcards)} Flashcards")
                        st.markdown("### All Flashcards")
                        
                        for i, card in enumerate(st.session_state.preview_flashcards, 1):
                            with st.expander(f"🧠 Flashcard {i}", expanded=False):
                                st.markdown(f"**Flashcard {i}:**")
                                st.markdown("")
                                st.markdown("**Front (Question):**")
                                st.write(card['front'])
                                st.markdown("")
                                st.markdown("**Back (Answer):**")
                                st.write(card['back'])
