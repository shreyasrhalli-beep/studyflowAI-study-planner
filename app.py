            generate_plan = st.form_submit_button(
                "✦ Generate my timetable", type="primary", use_container_width=True
            )

    if generate_plan:
        if not grade.strip() or not subjects.strip():
            st.warning("Please enter your grade and at least one subject.")
        else:
            total_minutes = int(round(float(available_hours) * 60))
            local_plan = make_local_timetable(
                subjects, weak_topics, available_hours, start_time, grade.strip(), exam_date
            )
            plan = None
            if get_api_key():
                prompt = f"""You are StudyFlow AI, a careful school study-planning assistant.
Create a realistic daily study timetable using the student's details below.

STUDENT DETAILS
Grade: {grade.strip()}
Subjects: {subjects}
Weak topics to prioritise: {weak_topics.strip() or "No specific weak topics listed"}
Total time available: exactly {total_minutes} minutes (breaks count inside this time)
Preferred start time: {start_time.strftime("%I:%M %p")}
Exam date: {exam_date.isoformat()}
Existing tasks: {json.dumps(st.session_state.tasks, ensure_ascii=False)}

OUTPUT RULES
- Return ONLY valid JSON. Do not use Markdown, code fences, or a Markdown table.
- Use exactly these top-level keys: overview, sessions, weekly_checklist, tips.
- sessions must be a list of objects with exactly these fields: type, duration_minutes, activity, subject, description.
- type must be either "study" or "break".
- The sum of every session's duration_minutes MUST equal exactly {total_minutes}.
- Add a 5-minute break between focus blocks for plans longer than 60 minutes.
- Keep study blocks at 45 minutes or less.
- Put weak topics early in the schedule and spend extra attention on them.
- Include concept learning, practice questions, active recall, and revision where time allows.
- Make every description specific: say what to read, solve, write, recall, or review.
- weekly_checklist must contain 4 to 6 short actionable items.
- tips must contain 2 or 3 concise study tips.

JSON SHAPE EXAMPLE
{{
  "overview": "A balanced routine for today's study goals.",
  "sessions": [
    {{"type":"study","duration_minutes":35,"activity":"Algebra focus","subject":"Maths","description":"Review the method, solve examples, and check each answer."}},
    {{"type":"break","duration_minutes":5,"activity":"Short break","subject":"Recharge","description":"Stretch, drink water, and rest your eyes."}}
  ],
  "weekly_checklist": ["Practise weak topics", "Review mistakes"],
  "tips": ["Keep your phone away", "Use active recall"]
}}
The example is only a shape. Create enough sessions for the full {total_minutes} minutes."""
                with st.spinner("✦ Gemini is building your personalised timetable..."):
                    ai_text = ask_ai(prompt, json_mode=True)
                plan = parse_ai_timetable(ai_text, total_minutes)
                if plan is None:
                    st.info("Gemini did not return a complete timetable this time, so StudyFlow built one from your inputs instead.")
            else:
                st.info("Your timetable will work without an API key. Add a Gemini key in AI Settings for AI-personalised session ideas.")
                plan = local_plan

            if plan is None:
                plan = local_plan
            plan["sessions"] = add_clock_times(plan["sessions"], start_time)
            plan["grade"] = grade.strip()
            plan["subjects"] = split_user_items(subjects)
            plan["exam_date"] = exam_date.isoformat()
            plan["available_minutes"] = total_minutes
            plan["start_time"] = start_time.strftime("%H:%M")
            st.session_state.last_study_plan = plan

    saved_plan = st.session_state.get("last_study_plan")
    if saved_plan:
        render_study_plan(saved_plan)
    else:
        with st.container(border=True):
            st.markdown("### Your timetable will appear here")
            st.markdown("<p class='muted'>Fill in your subjects and available time, then select <b>Generate my timetable</b>. You will get timed study blocks, short breaks, and a weekly checklist.</p>", unsafe_allow_html=True)

# ---------------- AI TUTOR ----------------
elif st.session_state.page == "AI Tutor":
    page_header("AI Tutor", "Your personal AI learning assistant.")
    st.markdown(
        f"<div class='panel'><b>✦ StudyFlow AI</b><span style='float:right;color:{GREEN}'>Gemini powered</span><br><span class='muted'>Ask me to explain a topic, solve a practice question or organise your revision.</span></div>",
        unsafe_allow_html=True,
    )

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask StudyFlow AI a question...")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        history = "\n".join(
            f"{'YOU' if item['role'] == 'user' else 'STUDYFLOW AI'}: {item['content']}"
            for item in st.session_state.chat_history[-12:]
        )
        prompt = f"""
You are StudyFlow AI, a friendly school tutor.
Help students understand concepts, solve academic questions,
prepare for exams and improve study habits.
Explain difficult concepts step by step.
Use simple language and examples.
Do not just give answers; explain the reasoning.
Be accurate and encouraging.

Conversation:
{history}

Answer the latest question.
"""
        with st.chat_message("assistant"):
            with st.spinner("StudyFlow AI is thinking..."):
                answer = ask_ai(prompt)
            st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

    st.caption("AI can make mistakes. Check important academic information.")
