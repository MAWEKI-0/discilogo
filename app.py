"""
Discilogo - Personal Habit Tracking App
Mobile-first Streamlit application for daily accountability.
"""

import streamlit as st
import pandas as pd
import database as db

# Page configuration
st.set_page_config(
    page_title="Discilogo",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Mobile-first custom CSS
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobile-first container */
    .block-container {
        padding: 1rem 1rem 4rem 1rem !important;
        max-width: 100% !important;
    }
    
    /* Large habit question text */
    .habit-question {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        text-align: center !important;
        padding: 2rem 1rem !important;
        color: #fafafa !important;
        line-height: 1.4 !important;
    }
    
    /* Full-width large buttons */
    .stButton > button {
        width: 100% !important;
        padding: 1.2rem 2rem !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        margin: 0.5rem 0 !important;
        min-height: 70px !important;
    }
    
    /* YES button styling */
    .yes-btn > button {
        background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%) !important;
        border: none !important;
        color: #0e1117 !important;
    }
    .yes-btn > button:hover {
        background: linear-gradient(135deg, #00e6b8 0%, #00cca0 100%) !important;
        transform: scale(1.02);
    }
    
    /* NO button styling */
    .no-btn > button {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important;
        border: none !important;
        color: #ffffff !important;
    }
    .no-btn > button:hover {
        background: linear-gradient(135deg, #ff5e4d 0%, #d44637 100%) !important;
    }
    
    /* Confirm failure button */
    .confirm-btn > button {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%) !important;
        border: none !important;
        color: #0e1117 !important;
    }
    
    /* Success/completion styling */
    .completion-box {
        background: linear-gradient(135deg, #1a1f2e 0%, #2d3748 100%);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
        border: 1px solid #00d4aa;
    }
    
    .streak-number {
        font-size: 4rem !important;
        font-weight: 700 !important;
        color: #00d4aa !important;
        display: block;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1 !important;
        padding: 1rem !important;
        font-size: 1rem !important;
    }
    
    /* Text input styling */
    .stTextArea textarea {
        font-size: 1.1rem !important;
        padding: 1rem !important;
        border-radius: 12px !important;
    }
    
    .stTextInput input {
        font-size: 1.1rem !important;
        padding: 1rem !important;
        border-radius: 12px !important;
    }
    
    /* Summary card */
    .summary-item {
        display: flex;
        justify-content: space-between;
        padding: 0.8rem 1rem;
        background: #1a1f2e;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ============== SESSION STATE INITIALIZATION ==============
if 'current_habit_index' not in st.session_state:
    st.session_state.current_habit_index = 0
if 'pending_habits' not in st.session_state:
    st.session_state.pending_habits = []
if 'show_excuse_input' not in st.session_state:
    st.session_state.show_excuse_input = False
if 'day_complete' not in st.session_state:
    st.session_state.day_complete = False


def refresh_pending_habits():
    """Refresh the list of pending habits for today."""
    st.session_state.pending_habits = db.get_pending_habits_today()
    st.session_state.current_habit_index = 0
    st.session_state.show_excuse_input = False
    if not st.session_state.pending_habits:
        st.session_state.day_complete = True
    else:
        st.session_state.day_complete = False


def log_yes():
    """Handle YES response."""
    habit = st.session_state.pending_habits[st.session_state.current_habit_index]
    db.log_habit(habit['id'], habit['question_text'], status=True)
    move_to_next_habit()


def show_excuse_input():
    """Show the excuse input field."""
    st.session_state.show_excuse_input = True


def log_no_with_excuse(excuse: str):
    """Handle NO response with excuse."""
    habit = st.session_state.pending_habits[st.session_state.current_habit_index]
    db.log_habit(habit['id'], habit['question_text'], status=False, excuse_note=excuse)
    st.session_state.show_excuse_input = False
    move_to_next_habit()


def move_to_next_habit():
    """Move to the next habit or mark day complete."""
    st.session_state.current_habit_index += 1
    st.session_state.show_excuse_input = False
    if st.session_state.current_habit_index >= len(st.session_state.pending_habits):
        st.session_state.day_complete = True


# ============== MAIN APP ==============

st.markdown("<h1 style='text-align: center; margin-bottom: 0.5rem;'>🎯 Discilogo</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; margin-bottom: 1.5rem;'>Daily Accountability</p>", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Daily Check", "⚙️ Manage", "📊 Data", "📝 Notes"])


# ============== TAB 1: DAILY CHECK ==============
with tab1:
    # Refresh pending habits
    if st.button("🔄 Refresh", key="refresh_btn", help="Check for new pending habits"):
        refresh_pending_habits()
        st.rerun()
    
    # Initialize on first load
    if not st.session_state.pending_habits and not st.session_state.day_complete:
        refresh_pending_habits()
    
    active_habits = db.get_active_habits()
    
    if not active_habits:
        st.markdown("---")
        st.info("👋 **Get started!**\n\nGo to the **Manage** tab to add your first habit.")
    
    elif st.session_state.day_complete:
        # Day complete - show summary
        st.markdown("---")
        streak = db.get_streak()
        today_logs = db.get_today_logs()
        
        st.markdown(f"""
        <div class="completion-box">
            <h2 style="margin: 0 0 1rem 0;">✅ Day Complete!</h2>
            <span class="streak-number">🔥 {streak}</span>
            <p style="color: #888; margin-top: 0.5rem;">day streak</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show today's summary
        if today_logs:
            st.markdown("### Today's Summary")
            for log in today_logs:
                status_icon = "✅" if log['status'] else "❌"
                excuse = f" — *{log['excuse_note']}*" if log['excuse_note'] else ""
                st.markdown(f"{status_icon} {log['habit_question_snapshot']}{excuse}")
        
        # Reset button for testing
        if st.button("🔄 Check Again", help="Re-check for any new habits"):
            st.session_state.day_complete = False
            refresh_pending_habits()
            st.rerun()
    
    else:
        # Show current habit wizard-style
        pending = st.session_state.pending_habits
        idx = st.session_state.current_habit_index
        
        if idx < len(pending):
            current_habit = pending[idx]
            
            # Progress indicator
            st.progress((idx) / len(pending))
            st.markdown(f"<p style='text-align: center; color: #888;'>Habit {idx + 1} of {len(pending)}</p>", unsafe_allow_html=True)
            
            # Question display
            st.markdown(f"<div class='habit-question'>{current_habit['question_text']}</div>", unsafe_allow_html=True)
            
            if not st.session_state.show_excuse_input:
                # YES / NO buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="yes-btn">', unsafe_allow_html=True)
                    if st.button("✓ YES", key="yes_btn", use_container_width=True):
                        log_yes()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="no-btn">', unsafe_allow_html=True)
                    if st.button("✗ NO", key="no_btn", use_container_width=True):
                        show_excuse_input()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            
            else:
                # Show excuse input
                st.markdown("---")
                st.markdown("### 😔 Why? (Be honest for the AI)")
                excuse = st.text_area(
                    "Your reason:",
                    placeholder="Explain what prevented you from completing this habit...",
                    key="excuse_input",
                    label_visibility="collapsed"
                )
                
                st.markdown('<div class="confirm-btn">', unsafe_allow_html=True)
                if st.button("📝 Confirm Failure", key="confirm_btn", use_container_width=True, disabled=not excuse):
                    if excuse and excuse.strip():
                        log_no_with_excuse(excuse.strip())
                        st.rerun()
                    else:
                        st.warning("Please provide a reason.")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Cancel button
                if st.button("← Back", key="back_btn"):
                    st.session_state.show_excuse_input = False
                    st.rerun()


# ============== TAB 2: MANAGE HABITS ==============
with tab2:
    st.markdown("### ➕ Add New Habit")
    
    with st.form("add_habit_form", clear_on_submit=True):
        new_habit = st.text_input(
            "Question Text",
            placeholder="e.g., Did you exercise today?",
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("Add Habit", use_container_width=True)
        
        if submitted and new_habit.strip():
            db.add_habit(new_habit.strip())
            st.success(f"✅ Added: *{new_habit}*")
            refresh_pending_habits()
            st.rerun()
        elif submitted:
            st.warning("Please enter a habit question.")
    
    st.markdown("---")
    st.markdown("### 📝 Your Habits")
    
    all_habits = db.get_all_habits()
    
    if not all_habits:
        st.info("No habits yet. Add one above!")
    else:
        for habit in all_habits:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                status = "🟢" if habit['is_active'] else "⚫"
                st.markdown(f"{status} {habit['question_text']}")
            
            with col2:
                if habit['is_active']:
                    if st.button("Archive", key=f"archive_{habit['id']}", help="Stop tracking this habit"):
                        db.archive_habit(habit['id'])
                        refresh_pending_habits()
                        st.rerun()
                else:
                    if st.button("Delete", key=f"delete_{habit['id']}", help="Permanently delete"):
                        db.delete_habit(habit['id'])
                        st.rerun()


# ============== TAB 3: RAW DATA ==============
with tab3:
    st.markdown("### 📊 Recent Entries (Last 10)")
    
    logs = db.get_recent_logs(10)
    
    if logs:
        df = pd.DataFrame(logs)
        df['status'] = df['status'].apply(lambda x: '✅ Yes' if x else '❌ No')
        df = df.rename(columns={
            'timestamp': 'Time',
            'date': 'Date',
            'habit_question_snapshot': 'Habit',
            'status': 'Status',
            'excuse_note': 'Note'
        })
        df = df[['Date', 'Habit', 'Status', 'Note']]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No data yet. Complete your first daily check!")
    
    # Stats
    st.markdown("---")
    st.markdown("### 📈 Quick Stats")
    
    col1, col2 = st.columns(2)
    with col1:
        streak = db.get_streak()
        st.metric("Current Streak", f"🔥 {streak} days")
    
    with col2:
        active_count = len(db.get_active_habits())
        st.metric("Active Habits", f"📋 {active_count}")


# ============== TAB 4: NOTES ==============
with tab4:
    st.markdown("### 📝 Quick Notes")
    
    # Add new note
    with st.form("add_note_form", clear_on_submit=True):
        new_note = st.text_area(
            "Write a note...",
            placeholder="Capture a thought, reflection, or reminder...",
            label_visibility="collapsed",
            height=100
        )
        submitted = st.form_submit_button("💾 Save Note", use_container_width=True)
        
        if submitted and new_note.strip():
            db.add_note(new_note.strip())
            st.success("✅ Note saved!")
            st.rerun()
        elif submitted:
            st.warning("Please write something first.")
    
    st.markdown("---")
    
    # Display existing notes
    notes = db.get_all_notes()
    
    if not notes:
        st.info("No notes yet. Add one above!")
    else:
        for note in notes:
            with st.container():
                # Note card styling
                st.markdown(f"""
                <div style="background: #1a1f2e; padding: 1rem; border-radius: 12px; margin-bottom: 0.8rem; border-left: 3px solid #00d4aa;">
                    <p style="margin: 0; color: #fafafa; white-space: pre-wrap;">{note['content']}</p>
                    <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.8rem;">{note['created_at'][:10]}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🗑️ Delete", key=f"del_note_{note['id']}", help="Delete this note"):
                    db.delete_note(note['id'])
                    st.rerun()
