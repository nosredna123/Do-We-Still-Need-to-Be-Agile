# FoodGuard: System Requirements

## Functional Requirements (RF)

- [cite_start]**[RF001] User Registration:** The system must collect and validate the user's full name, email, birth date, and password[cite: 37]. [cite_start]Access to the chat remains blocked at this stage[cite: 42].
- [cite_start]**[RF002] Anamnesis Registration:** The system automatically presents a health history form after user registration[cite: 47]. [cite_start]The chat and full platform features are only unlocked upon successful submission of this form[cite: 54].
- [cite_start]**[RF003 & RF004] Authentication & Password Recovery:** The system authenticates user credentials (email and password) via Firebase Authentication[cite: 59]. [cite_start]The password recovery flow utilizes Firebase's automated reset link emails[cite: 68].
- [cite_start]**[RF005 & RF006] Home Navigation:** The home screen features navigation for "Who we are" and "How it works"[cite: 76]. [cite_start]Clicking "Let's begin" redirects unauthenticated users to login and authenticated users directly to the Chat screen[cite: 81, 82].
- [cite_start]**[RF007] New Chat Creation:** The system features a "New conversation" button in the sidebar that generates a blank chat page[cite: 87, 88].
- [cite_start]**[RF008] Text Interaction:** The system processes text input, cross-references it with the logged-in user's anamnesis, and displays an LLM-generated response[cite: 101, 102]. [cite_start]The input field and send button are disabled during processing[cite: 103].
- [cite_start]**[RF009] Image Interaction:** The system processes images via `zbar-wasm` to extract barcodes[cite: 109]. [cite_start]It consults an external food API to fetch ingredients, cross-references this with the user's anamnesis, and generates an LLM response[cite: 112, 113].
- [cite_start]**[RF011, RF012 & RF013] Chat Management:** The system displays a sidebar with chat history[cite: 128]. [cite_start]Users can edit their last prompt to regenerate a response[cite: 134, 135]. [cite_start]Users can permanently delete selected conversations[cite: 144].
- [cite_start]**[RF014, RF015 & RF016] Profile & Anamnesis Editing:** A profile modal displays user information and health data separately[cite: 151, 159, 179]. [cite_start]Editing the anamnesis form automatically blocks further prompts in older chats, forcing the creation of a new chat for updated context[cite: 180].
- [cite_start]**[RF017] Logout:** The system must invalidate the authentication token upon confirmation and redirect the user to the home page[cite: 192].

## Quality Requirements (RQ)

- [cite_start]**[RQ001] Usability:** Visual UI feedback (like error toasts) must appear within 500 milliseconds of user interaction[cite: 200].
- [cite_start]**[RQ002] Security & Privacy:** Passwords are hashed and managed by Firebase Authentication[cite: 207]. [cite_start]The internal routing system masks or removes identifying fields (Name, Email, Birth Date) before sending anamnesis data to the LLM[cite: 208, 212]. [cite_start]Sessions automatically expire after 24 hours of inactivity[cite: 213].
- [cite_start]**[RQ003] Performance:** Text-based prompt responses must not exceed 15 seconds[cite: 219]. [cite_start]Local barcode extraction processing must not exceed 8 seconds before triggering an error fallback[cite: 220, 221].
- [cite_start]**[RQ004] Persistence:** Chat messages and context are saved in real-time to prevent data loss if the tab is accidentally closed[cite: 226].

## Business Rules (RN)

- [cite_start]**[RN001] Mandatory Anamnesis:** The anamnesis form is strictly required; users abandoning registration before filling it out are forced to complete it upon their next login[cite: 234, 235].
- [cite_start]**[RN002] Image Validation:** The system only accepts a single image in PNG, JPEG, or JPG format, with a maximum size of 10MB[cite: 239].
- [cite_start]**[RN003] Text Limits:** Text prompts and user inputs are strictly limited to 5,000 characters to ensure NLP performance[cite: 242].
- [cite_start]**[RN004] Health Integrity:** Altering the anamnesis invalidates previous chats to ensure all AI advice utilizes the most up-to-date health context[cite: 245].
- [cite_start]**[RN005 & RN006] Data Privacy:** Passwords are never stored in plain text[cite: 248]. [cite_start]Health data is strictly for LLM prompt composition and is prohibited from being shared with third parties or advertising APIs[cite: 252, 256].
- [cite_start]**[RN007] Session Control:** Accessing chat history or profile editing requires an active session; direct URL access without authentication redirects to the Home or Login screen[cite: 259, 260].
- [cite_start]**[RN008 & RN014] Processing Debounce:** Inputs are disabled and a loading state is shown during LLM processing or barcode reading to prevent duplicate submissions[cite: 263]. [cite_start]The inputs are re-enabled only after the response is completely rendered[cite: 286].
- [cite_start]**[RN009] Context Persistence:** Loading an old chat rebuilds and sends the entire message context of that specific branch to the LLM[cite: 266].
- [cite_start]**[RN011, RN012 & RN013] Field Validations:** Emails must follow standard formatting and be unique[cite: 273]. [cite_start]Passwords require at least 8 characters, including uppercase, lowercase, and numbers[cite: 276]. [cite_start]Names are limited to 250 characters and reject numbers or special symbols[cite: 282, 283].
