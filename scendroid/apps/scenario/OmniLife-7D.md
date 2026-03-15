Below is my preliminary solution for a one-week scenario I created; please implement it for me. Note: Most tasks in this one-week scenario can directly reuse existing implementations from our current scenarios a/b/c/d/e; prioritize reusing them, and only implement new initialization or evaluation logic if no suitable existing implementation is available. Key considerations I have identified for building and running this scenario include: (1) During environment initialization, ensure the system date is updated accordingly after crossing days. (2) Maximize reuse of existing implementations from scenarios a/b/c/d/e (including instruction, initialization, and evaluation logic). I have already indicated which task each subtask can reuse in its title, but you must also verify carefully to avoid errors. (3) Carefully consider the initialization and evaluation logic.  

Week-Long Scenario v2 (72 tasks)
Day 1 (Monday) = Scenario a (Busy Monday, complex weekday workflow) + WeekPlan preference anchor + Starting point for meeting progress tracking  

Objective: Establish a preference anchor + Establish cross-day trackable status for ).replace(u201d, Meeting A" (attendees/notes/progress)  

W1-01 Adjust weekday alarm (reuse a-1 / A1)  
Record: weekday_alarm_time, alarm_shift_minutes  

W1-02 Check morning schedule (reuse a-2 / A2, QA)  
Record: morning_items[], mentioned_meeting=true/false, mentioned_package=true/false  

W1-03 Extract attendees for the 11:30 weekly meeting (reuse a-3 / A4, QA)  
Record: meetingA={title,time,loc,attendees[]}, last_attendees  

W1-04 Send group meeting reminder (reuse a-4 / A5)  
Introduce distractor: John vs. Johnathan  
Record: meetingA_notified_count, forbidden_contact_sent=false/true  

W1-05 Create meeting minutes template in Markor (reuse a-5 / A6, WorkLog.md)  
Record: artifact_worklog_created=true  

✅ W1-06 New: Create WeekPlan.md (preference anchor)  
Write rules (verifiable):  

diet: light / no fried (optional: no dairy)  

budget: weekly dining <= 120;non-essential > 100 ask-first

exercise: 18:30, 30 minutes; conflicts must trigger reminders and provide solutions  
Record: preferences={diet,budget,exercise}, artifact_weekplan_created=true  

W1-07 Place shopping order (desk) (reuse a-7 / A8)  
Record: orderA={sku,amount,ship_address,order_id?}  

W1-08 Record expense (linked to order amount) (reuse a-8 / A9)  
Record: expenseA={amount,category}, weekly_spend_total+=amount  

✅ W1-09 New: First ).replace(u201d, collect RSVP progress from meeting attendees" before Meeting A (Message QA / reuse scenario c-8)  
Instruction: ).replace(u201d, Check who among those four people has replied, and summarize it in one sentence for me."  
Evaluation: Count only conversations related to meetingA; exclude casual chat and Emily.  
Record: meetingA_rsvp={John:?,Bob:?,...}, meetingA_progress_summary_v1  

W1-10 Append daily summary to WorkLog (reuse a-10 / A12)  
Must include: meetingA + today's expense (expenseA)  
Record: worklog_appended_day1=true  

Number of Day 1 tasks: 10  

Day 2 (Tuesday) = Scenario c (Student/Research day), adapted into a ).replace(u201d, memory-misdirection trap day" + Second tracking of Meeting A progress  

Objective: Extensive use of anaphoric references such as ).replace(u201d, that/they/earlier"; deliberately introduce similar meeting titles to induce incorrect reuse of Day 1 attendees  

W2-01 Set alarm + create new Seminar event (reuse c-1)  
Trap title design: Also named ).replace(u201d, Weekly Seminar"  
Record: seminar={title,time,loc,attendees[]}  

W2-02 Set up high-quality audio recording and start audio recording (reuse c-2)  
Record: audio_tue_raw=true  

W2-03 View receipt image → record expense (reuse c-3, enforce Files/Download)  
Record: expense_tue_breakfast={amount}, weekly_spend_total+=amount

W2-04 Rename and move the audio recording to the Lectures folder (reuse c-4)
Record: audio_tue_file={name,path}

✅ W2-05 Modify the time of ).replace(u201d, this morning's seminar" and send a notification (reuse c-5, but adjust the reference)
Instruction: ).replace(u201d, Delay the seminar we created this morning by 1 hour, then notify the attendees."
Evaluation: Notify only seminar_attendees; meetingA_attendees is forbidden.
Record: seminar_time_updated=true, seminar_notified_count, wrong_group_notified=false/true

✅ W2-06 Shopping (USB drive) (reuse c-6)
Trigger rule: If price > 100 → ask-first (clarification required)
Record: orderB={sku,amount,necessity?}, ask_before_buy_triggered=true/false

✅ W2-07 Exercise preparation (music playlist + OpenTracks) (reuse c-7)
Align with WeekPlan: Conflict check at 18:30
Record: exercise_started=true/false, conflict_checked=true/false

W2-08 Summarize SMS replies into Markor (reuse c-8)
Trap: SMS messages contain casual chat about meetingA; do not write into seminar_progress
Record: seminar_progress_summary

W2-09 DailySchedule.md (reuse c-9)
Record: artifact_dailyschedule_created=true

W2-10 Append the audio recording filename to the summary (reuse c-10)
Record: audio_referenced_in_doc=true

✅ W2-11 New: Track Meeting A progress for the second time (Message QA)
Instruction: ).replace(u201d, While you're at it, check yesterday's weekly meeting notification and see who hasn't replied yet."
Evaluation: Must lock onto the meetingA group; must not mistakenly count seminar attendees.
Record: meetingA_progress_summary_v2, meetingA_pending_list[]

Day 2 task count: 11 (cumulative total: 21)

Day 3 (Wednesday) = scenario d (business trip Day 1) + multi-source time conflicts (image vs. calendar) + strong dependency on ).replace(u201d, address reuse"

Goal: Solidify spatiotemporal contradictions and transform the address from the image into a cross-task anchor point

W3-01 World Clock + Extract flight times from image → write into calendar (reuse d-E1)
Record: trip={city,tz}, flight_from_image={dep,arr,number}

✅ W3-02 New: Inject and resolve conflicts
Calendar already contains ).replace(u201d, Flight to X", but with a different time
Task: Identify the conflict → update to the image time → log one line in WorkLog: ).replace(u201d, Corrected"
Record: flight_conflict_fixed=true, worklog_conflict_note=true

W3-03 One-time alarm + Highest-priority task list (reuse d-E2)
Record: trip_alarm_set=true, trip_tasks_top=true

W3-04 Bluetooth + Do Not Disturb (DND) (reuse d-E3)
Record: bluetooth_on=true, dnd_on=true

W3-05 Shopping: USB drive, address sourced from trip image (reuse d-E4)
Record: orderC={amount,address_from_image=true}

W3-06 Contact → share hotel front desk phone number via SMS (reuse d-E5)
Record: hotel_contact_shared=true

W3-07 Meeting audio recording configuration + rename (reuse d-E6)
Log: audio_wed_keynote={name}

W3-08 Take receipt photo → archive into file folder (reuse d-E7)
Log: receipts_folder_created=true, receipt_files_count+=1

W3-09 Record three expenses + TripSummary.md (reuse d-E8/E9)
Log: expense_trip_day1_total, artifact_trip_summary_created=true

W3-10 QA for total expenses over the past 3 days (reuse d-E10, window Mon–Wed)
Log: spend_3day_total

✅ W3-11 New: Write ).replace(u201d, business trip address" into Contacts (contact: Office Reception)
For reuse on Friday
Log: contact_office_reception_created=true

Day 3 task count: 11 (cumulative 32)

Day 4 (Thursday) = Business Trip Day 2 (extended) + high-pressure preference/budget test + cross-app chain ).replace(u201d, Calendar→Clock"

Goal: Increase difficulty without relying on new apps—leverage rules and cross-app linkages; supplement task count

W4-01 Retrieve total expenses for the last 2 days (variant reuse of d-E10)
Log: spend_last2days

✅ W4-02 If budget exceeded: write two cost-control plans (new task, Markor append to WeekPlan or WorkLog)
Log: budget_plan_written=true

W4-03 From Calendar, locate today's afternoon keynote → set up audio recording reminder alarm (cross-app Calendar→Clock, new task)
Log: keynote_alarm_set=true, alarm_time

✅ W4-04 18:30 exercise conflict: Provide solution (multi-path selection)
Path A: Delay exercise and log in WorkLog
Path B: Shorten by 15 minutes and log in WorkLog
Log: exercise_plan_choice=A/B, worklog_updated=true

W4-05 Take receipt photo and archive (reuse d-E7 again)
Log: receipt_files_count+=1

W4-06 Append TripSummary: today's key event + budget status (reuse d-E9 append)
Log: trip_summary_appended_day2=true

✅ W4-07 New: Extract ).replace(u201d, return flight number/time tomorrow" from image or email screenshot (Files) and save into Markor
(If you lack an email app, use a preloaded return-info image in Files.)
Log: return_flight_info_saved=true

✅ W4-08 New: Send SMS to colleague confirming ).replace(u201d, I'll be traveling tomorrow" and include return time (Contacts→SMS)
Log: return_trip_notified=true

Day 4 task count: 8 (cumulative 40)

Day 5 (Friday) = Return to work + Pre-weekend: advance Meeting B (new meeting) + rule ).replace(u201d, ask first, then buy" trap + final closure of Meeting A

Goal: On this day, perform more ).replace(u201d, progress tracking/summarization/follow-up", and introduce a second meeting B to establish ).replace(u201d, tracking multiple meetings"

W5-01 Check next Monday's calendar (new task, Calendar QA)
Includes one Meeting B (title similar to meetingA: Weekly Sync)
Log: meetingB={title,time,loc,attendees[]}

✅ W5-02 Send SMS: notify only Meeting B attendees (new task Calendar→Contacts→SMS)
Trap: Cannot use the group of people from meetingA or seminar.
Record: meetingB_notified_count, wrong_group_notified=false/true

✅ W5-03 Meeting B Progress Tracking (1st time) (Message QA)
Instruction: ).replace(u201d, Check whether they confirmed after the reminder and summarize in one sentence."
Record: meetingB_rsvp, meetingB_progress_summary_v1

✅ W5-04 Shopping: Supplies (if price trigger >100, ask first)
This is the ).replace(u201d, theft vs. death penalty"-style trap you mentioned:
Memory says ).replace(u201d, I often place orders directly," but the rule requires ).replace(u201d, ask first."
Record: orderD={amount,necessity}, ask_before_buy_triggered=true/false

W5-05 Expense Tracking: Categorize today's shopping as Non-essential and write the reason (new task: Expense+Markor)
Record: expense_nonessential_added=true

W5-06 Friday Night: Disable Saturday morning alarm (reuse variant b-1)
Requirement: Disable only the Saturday morning alarm; do not modify weekday alarms.
Record: sat_alarm_disabled=true

✅ W5-07 New: Meeting A Progress Tracking (3rd time) + Wrap-up
Instruction: ).replace(u201d, Summarize three pending task progress items related to Monday's meeting and append them to the end of WorkLog."
Evaluation: Must reference the meetingA title/time or at least two participant names as anchors.
Record: meetingA_final_summary_written=true

✅ W5-08 New: Write the agenda framework for meetingB into WorkLog (similar to outline A6, but specific to meetingB)
Record: meetingB_outline_created=true

Day 5 task count: 8 (cumulative total: 48)

Day 6 (Saturday) = scenario b (weekend cooking + photos + shopping + exercise + weekend summary), with enhanced ).replace(u201d, preference constraints"

Goal: Increase weekend tasks while enforcing WeekPlan diet/budget continuity constraints; additionally, add ).replace(u201d, progress tracking for recurring tasks" to meet volume requirements.

W6-01 Turn off Saturday morning alarm (reuse b-1; can serve as consistency check with W5-06)
Record: sat_alarm_off_confirmed=true

W6-02 Recipe search (reuse b-2)
New constraint: Must comply with light / no fried (optional: no dairy)
Record: recipe_selected, constraints_satisfied=true/false

W6-03 Markor writes SaturdayBreakfast.md (reuse b-3)
Record: sat_breakfast_doc_created=true

W6-04 Timer starts counting down based on prep time (reuse b-4)
Record: timer_started=true, prep_time_minutes

W6-05 Camera takes breakfast photo and archives it (reuse b-5)
Record: breakfast_photo_saved=true, photo_path

W6-06 Send a meeting SMS to a friend (reuse b-6)
Record: friend_meet_sms_sent=true

W6-07 Weekend bulk shopping order (reuse b-7)
Enhanced rule: If non-essential and amount >100, must ask first; essentials may be purchased directly.
Record: weekend_order={amount,necessity}, ask_before_buy_triggered=true/false

W6-08 Expense tracking (reuse b-8)
Record: expense_weekend_purchase_added=true, weekly_spend_total+=amount

W6-09 OpenTracks records a walk/exercise (reusing b-9)
Record: sat_walk_saved=true, walk_distance_or_duration

✅ W6-10 New: Send an SMS message ).replace(u201d, I've arrived" or ).replace(u201d, I'm on my way" to someone after the walk (OpenTracks→SMS, cross-app)
Record: arrival_sms_sent=true

W6-11 Weekend summary (reusing b-10, Markor appends weekendsummary)
Requirement: Append one sentence summarizing remaining weekly budget + one sentence summarizing today's exercise
Record: weekend_summary_appended=true

Day 6 task count: 11 (cumulative total: 59)

Day 7 (Sunday) = scenario e (hiking/picnic/photo deduplication/weekly expense/travel log) + ).replace(u201d, full-week closure" + second progress tracking for meetingB

Goal: Weekly statistics + causal consistency closure; and perform meetingB progress tracking again (occurs multiple times)

W7-01 Write picnic checklist into Tasks and check off existing items (reusing e-F1)
Existing supplies originate from the W6-07 order (pre-configurable)
Record: picnic_checklist_done=true, items_checked_count

W7-02 Change event location and send notification (reusing e-F2, Calendar+SMS)
Record: event_location_updated=true, attendees_notified=true

W7-03 Retroactively create a sequential playlist (reusing e-F3)
Record: playlist_created=true

W7-04 OpenTracks starts recording + shuffle playlist (reusing e-F4)
Record: sun_hike_started=true

W7-05 Camera records video (reusing e-F5)
Record: video_saved=true

W7-06 Purchase meat alternatives for $100–$200 (reusing e-F6)
Strict rule: Non-essential purchases exceeding $100 must first trigger an inquiry (otherwise fail)
Record: orderE={amount}, ask_before_buy_triggered=true/false

W7-07 OpenTracks daily + weekly statistics QA (reusing e-F7)
Record: weekly_hike_stats={distance,duration?}

W7-08 Files: photo deduplication + categorization (reusing e-F8)
Require folder to follow Saturday structure (causal consistency)
Record: photo_dedup_done=true, folders_created[]

W7-09 Expense: Record meat alternative purchase + answer weekly total expense QA (reusing e-F9)
Key: Total expense must reflect whether W7-06 purchase was skipped due to the rule-triggered inquiry (i.e., total differs if not purchased)
Record: weekly_spend_total_reported, expense_added_today=true/false

✅ W7-10 New: Second meetingB progress tracking (Message QA)
Instruction: ).replace(u201d, Also check next Monday's meeting—has anyone not yet confirmed?"
Record: meetingB_progress_summary_v2, meetingB_pending_list

✅ W7-11 New: Generate WeekReview.md (full-week closure)
Must include:

Compliance status for three preferences (diet/budget/exercise)

At least one conflict (flight time conflict or 6:30 PM conflict) and its resolution

What is the largest expense, and does it trigger ).replace(u201d, Ask First"?

Two improvements for next week (write back to WeekPlan or WeekReview)
Record: weekreview_created=true, habits_updated=true

✅ W7-12 Added: Sync the two improvements from WeekReview to WeekPlan.md (Markor edit)
Record: weekplan_updated=true
