export type SupportedLanguage = 'English' | 'Hindi' | 'Tamil' | 'Telugu' | 'Marathi';

export const TRANSLATIONS: Record<SupportedLanguage, Record<string, string>> = {
  "English": {
    "title": "QUANTUM CROP INTELLIGENCE",
    "subtitle": "Agricultural crop suitability analysis for Indian farmlands",
    "soil_nutrients": "SOIL NUTRIENTS",
    "climate_env": "CLIMATE & ENVIRONMENT",
    "generate_btn": "GENERATE REPORT",
    "awaiting": "Awaiting Field Data",
    "awaiting_sub": "Adjust parameters above, then click Generate Report.",
    "recommended": "RECOMMENDED CROP",
    "confidence": "CONFIDENCE",
    "season": "SEASON",
    "water_need": "WATER NEED",
    "ideal_soil": "IDEAL SOIL",
    "alternative": "ALTERNATIVE SUITABILITY",
    "insights": "FIELD INSIGHTS & ANALYSIS",
    "nitrogen": "Nitrogen (N)",
    "phosphorus": "Phosphorus (P)",
    "potassium": "Potassium (K)",
    "temperature": "Temperature (°C)",
    "humidity": "Humidity (%)",
    "ph": "Soil pH",
    "rainfall": "Rainfall (mm)",
    "computing": "COMPUTING QUANTUM STATEVECTORS...",
    "language": "Language",
    "optimal": "Optimal Parameters",
    "attention": "Parameters Requiring Attention",
    "probability_dist": "Probability Distribution",
    "crop": "Crop",
    "probability": "Probability (%)",
    "empty_placeholder": "Adjust parameters in the field conditions panel to analyze crop suitability.",
    "match_score": "Match score",
    "match_score_footnote": "Derived from the model's decision scores; not a calibrated probability.",
    "agronomic_footnote": "General guidance, not agronomic advice.",
    "your_inputs": "Your inputs",
    "within_range": "Within range",
    "near_edge": "Near edge",
    "about_model": "About this model",
    "num_qubits": "Quantum qubits",
    "reps": "Circuit repetitions",
    "c_penalty": "C (penalty)",
    "inputs_changed": "Inputs changed since last analysis",
    "retry": "Retry",
    "error_unreachable": "Could not connect to the server.",
    "error_timeout": "Request timed out.",
    "error_server": "Server error or model not loaded.",
    "error_invalid_input": "Invalid input values.",
    "error_malformed": "Received malformed data from the server.",
    "analyze": "Analyze",
    "loading": "Analyzing field data...",
    "alternatives": "Alternatives"
  },
  "Hindi": {
    "title": "क्वांटम फसल बुद्धिमत्ता",
    "subtitle": "भारतीय कृषि भूमि के लिए फसल उपयुक्तता विश्लेषण",
    "soil_nutrients": "मिट्टी के पोषक तत्व",
    "climate_env": "जलवायु और पर्यावरण",
    "generate_btn": "रिपोर्ट बनाएं",
    "awaiting": "डेटा की प्रतीक्षा है",
    "awaiting_sub": "ऊपर पैरामीटर सेट करें और फिर रिपोर्ट बनाएं पर क्लिक करें।",
    "recommended": "अनुशंसित फसल",
    "confidence": "संभावना",
    "season": "मौसम",
    "water_need": "पानी की जरूरत",
    "ideal_soil": "आदर्श मिट्टी",
    "alternative": "वैकल्पिक उपयुक्तता",
    "insights": "क्षेत्र विश्लेषण",
    "nitrogen": "नाइट्रोजन (N)",
    "phosphorus": "फास्फोरस (P)",
    "potassium": "पोटैशियम (K)",
    "temperature": "तापमान (°C)",
    "humidity": "नमी (%)",
    "ph": "मिट्टी का पीएच",
    "rainfall": "बारिश (mm)",
    "computing": "क्वांटम स्थिति की गणना की जा रही है...",
    "language": "भाषा",
    "optimal": "इष्टतम पैरामीटर",
    "attention": "ध्यान देने योग्य पैरामीटर",
    "probability_dist": "संभावना वितरण",
    "crop": "फसल",
    "probability": "संभावना (%)",
    "empty_placeholder": "फसल उपयुक्तता का विश्लेषण करने के लिए क्षेत्र की स्थिति पैनल में पैरामीटर समायोजित करें।",
    "match_score": "मैच स्कोर",
    "match_score_footnote": "मॉडल के निर्णय स्कोर से लिया गया; कैलिब्रेट की गई संभावना नहीं।",
    "agronomic_footnote": "सामान्य मार्गदर्शन, कृषि संबंधी सलाह नहीं।",
    "your_inputs": "आपके इनपुट",
    "within_range": "सीमा के भीतर",
    "near_edge": "किनारे के पास",
    "about_model": "इस मॉडल के बारे में",
    "num_qubits": "क्वांटम क्विबिट्स",
    "reps": "सर्किट पुनरावृत्ति",
    "c_penalty": "सी (जुर्माना)",
    "inputs_changed": "अंतिम विश्लेषण के बाद से इनपुट बदल गए हैं",
    "retry": "पुनः प्रयास करें",
    "error_unreachable": "सर्वर से कनेक्ट नहीं हो सका।",
    "error_timeout": "अनुरोध का समय समाप्त हो गया।",
    "error_server": "सर्वर त्रुटि या मॉडल लोड नहीं हुआ।",
    "error_invalid_input": "अमान्य इनपुट मान।",
    "error_malformed": "सर्वर से विकृत डेटा प्राप्त हुआ।",
    "analyze": "विश्लेषण करें",
    "loading": "क्षेत्र डेटा का विश्लेषण कर रहा है...",
    "alternatives": "विकल्प"
  },
  "Tamil": {
    "title": "குவாண்டம் பயிர் நுண்ணறிவு",
    "subtitle": "இந்திய விவசாய நிலங்களுக்கான பயிர் பொருத்த பகுப்பாய்வு",
    "soil_nutrients": "மண் ஊட்டச்சத்துக்கள்",
    "climate_env": "காலநிலை & சுற்றுச்சூழல்",
    "generate_btn": "அறிக்கையை உருவாக்கு",
    "awaiting": "தரவுக்காக காத்திருக்கிறது",
    "awaiting_sub": "மேலே அளவுருக்களை அமைத்து, அறிக்கையை உருவாக்கு என்பதை கிளிக் செய்யவும்.",
    "recommended": "பரிந்துரைக்கப்படும் பயிர்",
    "confidence": "நம்பிக்கை",
    "season": "பருவம்",
    "water_need": "நீர் தேவை",
    "ideal_soil": "சிறந்த மண்",
    "alternative": "மாற்று பொருத்தம்",
    "insights": "கள நுண்ணறிவு மற்றும் பகுப்பாய்வு",
    "nitrogen": "நைட்ரஜன் (N)",
    "phosphorus": "பாஸ்பரஸ் (P)",
    "potassium": "பொட்டாசியம் (K)",
    "temperature": "வெப்பநிலை (°C)",
    "humidity": "ஈரப்பதம் (%)",
    "ph": "மண் pH",
    "rainfall": "மழை (mm)",
    "computing": "குவாண்டம் நிலையை கணக்கிடுகிறது...",
    "language": "மொழி",
    "optimal": "உகந்த அளவுருக்கள்",
    "attention": "கவனம் தேவைப்படும் அளவுருக்கள்",
    "probability_dist": "நிகழ்தகவு பரவல்",
    "crop": "பயிர்",
    "probability": "நிகழ்தகவு (%)",
    "empty_placeholder": "பயிர் பொருத்தத்தை பகுப்பாய்வு செய்ய கள நிலைமைகள் பேனலில் அளவுருக்களை சரிசெய்யவும்.",
    "match_score": "பொருத்த மதிப்பெண்",
    "match_score_footnote": "மாதிரியின் முடிவு மதிப்பெண்களிலிருந்து பெறப்பட்டது; அளவீடு செய்யப்பட்ட நிகழ்தகவு அல்ல.",
    "agronomic_footnote": "பொதுவான வழிகாட்டுதல், விவசாய ஆலோசனை அல்ல.",
    "your_inputs": "உங்கள் உள்ளீடுகள்",
    "within_range": "வரம்பிற்குள்",
    "near_edge": "விளிம்பிற்கு அருகில்",
    "about_model": "இந்த மாதிரியைப் பற்றி",
    "num_qubits": "குவாண்டம் குவிட்கள்",
    "reps": "சுற்று மறுபடியும்",
    "c_penalty": "சி (அபராதம்)",
    "inputs_changed": "கடைசி பகுப்பாய்விற்குப் பிறகு உள்ளீடுகள் மாறிவிட்டன",
    "retry": "மீண்டும் முயற்சிக்கவும்",
    "error_unreachable": "சேவையகத்துடன் இணைக்க முடியவில்லை.",
    "error_timeout": "கோரிக்கை நேரம் முடிந்தது.",
    "error_server": "சேவையகப் பிழை அல்லது மாதிரி ஏற்றப்படவில்லை.",
    "error_invalid_input": "தவறான உள்ளீட்டு மதிப்புகள்.",
    "error_malformed": "சேவையகத்திலிருந்து தவறான தரவு பெறப்பட்டது.",
    "analyze": "பகுப்பாய்வு",
    "loading": "கள தரவை பகுப்பாய்வு செய்கிறது...",
    "alternatives": "மாற்று"
  },
  "Telugu": {
    "title": "క్వాంటం పంట ఇంటెలిజెన్స్",
    "subtitle": "భారతీయ వ్యవసాయ భూములకు పంట అనుకూలత విశ్లేషణ",
    "soil_nutrients": "నేల పోషకాలు",
    "climate_env": "వాతావరణం & పర్యావరణం",
    "generate_btn": "రిపోర్ట్ సృష్టించండి",
    "awaiting": "డేటా కోసం వేచి ఉంది",
    "awaiting_sub": "పైన పారామితులను సెట్ చేసి రిపోర్ట్ సృష్టించండి క్లిక్ చేయండి.",
    "recommended": "సిఫార్సు చేయబడిన పంట",
    "confidence": "విశ్వాసం",
    "season": "సీజన్",
    "water_need": "నీటి అవసరం",
    "ideal_soil": "ఆదర్శ నేల",
    "alternative": "ప్రత్యామ్నాయ అనుకూలత",
    "insights": "ఫీల్డ్ విశ్లేషణ",
    "nitrogen": "నైట్రోజన్ (N)",
    "phosphorus": "భాస్వరం (P)",
    "potassium": "పొటాషియం (K)",
    "temperature": "ఉష్ణోగ్రత (°C)",
    "humidity": "తేమ (%)",
    "ph": "నేల pH",
    "rainfall": "వర్షపాతం (mm)",
    "computing": "క్వాంటం స్థితిని లెక్కిస్తోంది...",
    "language": "భాష",
    "optimal": "అనుకూల పారామితులు",
    "attention": "శ్రద్ధ వహించాల్సిన పారామితులు",
    "probability_dist": "సంభావ్యత పంపిణీ",
    "crop": "పంట",
    "probability": "సంభావ్యత (%)",
    "empty_placeholder": "పంట అనుకూలతను విశ్లేషించడానికి ఫీల్డ్ కండిషన్స్ ప్యానెల్‌లో పారామితులను సర్దుబాటు చేయండి.",
    "match_score": "మ్యాచ్ స్కోర్",
    "match_score_footnote": "మోడల్ నిర్ణయ స్కోర్‌ల నుండి తీసుకోబడింది; క్రమాంకనం చేయబడిన సంభావ్యత కాదు.",
    "agronomic_footnote": "సాధారణ మార్గదర్శకత్వం, వ్యవసాయ సలహా కాదు.",
    "your_inputs": "మీ ఇన్‌పుట్‌లు",
    "within_range": "పరిధిలో",
    "near_edge": "అంచు సమీపంలో",
    "about_model": "ఈ మోడల్ గురించి",
    "num_qubits": "క్వాంటం క్విబిట్స్",
    "reps": "సర్క్యూట్ పునరావృత్తులు",
    "c_penalty": "సి (పెనాల్టీ)",
    "inputs_changed": "చివరి విశ్లేషణ నుండి ఇన్‌పుట్‌లు మారాయి",
    "retry": "మళ్ళీ ప్రయత్నించండి",
    "error_unreachable": "సర్వర్‌కి కనెక్ట్ కాలేదు.",
    "error_timeout": "అభ్యర్థన సమయం ముగిసింది.",
    "error_server": "సర్వర్ లోపం లేదా మోడల్ లోడ్ కాలేదు.",
    "error_invalid_input": "చెల్లని ఇన్‌పుట్ విలువలు.",
    "error_malformed": "సర్వర్ నుండి తప్పుగా ఉన్న డేటా స్వీకరించబడింది.",
    "analyze": "విశ్లేషించండి",
    "loading": "ఫీల్డ్ డేటాను విశ్లేషిస్తోంది...",
    "alternatives": "ప్రత్యామ్నాయాలు"
  },
  "Marathi": {
    "title": "क्वांटम पीक बुद्धिमत्ता",
    "subtitle": "भारतीय शेतजमिनीसाठी पीक अनुकूलता विश्लेषण",
    "soil_nutrients": "मातीतील पोषक तत्वे",
    "climate_env": "हवामान आणि पर्यावरण",
    "generate_btn": "अहवाल तयार करा",
    "awaiting": "डेटाची प्रतीक्षा आहे",
    "awaiting_sub": "वर पॅरामीटर्स सेट करा आणि अहवाल तयार करा वर क्लिक करा.",
    "recommended": "शिफारस केलेले पीक",
    "confidence": "संभाव्यता",
    "season": "हंगाम",
    "water_need": "पाण्याची गरज",
    "ideal_soil": "आदर्श माती",
    "alternative": "पर्यायी अनुकूलता",
    "insights": "क्षेत्र विश्लेषण",
    "nitrogen": "नायट्रोजन (N)",
    "phosphorus": "फॉस्फरस (P)",
    "potassium": "पोटॅशियम (K)",
    "temperature": "तापमान (°C)",
    "humidity": "आर्द्रता (%)",
    "ph": "मातीचा सामू (pH)",
    "rainfall": "पाऊस (mm)",
    "computing": "क्वांटम स्थितीची गणना करत आहे...",
    "language": "भाषा",
    "optimal": "इष्टतम पॅरामीटर्स",
    "attention": "लक्ष देण्याची आवश्यकता असलेले पॅरामीटर्स",
    "probability_dist": "संभाव्यता वितरण",
    "crop": "पीक",
    "probability": "संभाव्यता (%)",
    "empty_placeholder": "पीक योग्यतेचे विश्लेषण करण्यासाठी फील्ड अटी पॅनेलमध्ये पॅरामीटर्स समायोजित करा.",
    "match_score": "सामना स्कोअर",
    "match_score_footnote": "मॉडेलच्या निर्णय स्कोअरमधून प्राप्त; कॅलिब्रेटेड संभाव्यता नाही.",
    "agronomic_footnote": "सामान्य मार्गदर्शन, कृषी सल्ला नाही.",
    "your_inputs": "तुमचे इनपुट",
    "within_range": "श्रेणीत",
    "near_edge": "काठाजवळ",
    "about_model": "या मॉडेल बद्दल",
    "num_qubits": "क्वांटम क्यूबिट्स",
    "reps": "सर्किट पुनरावृत्ती",
    "c_penalty": "सी (दंड)",
    "inputs_changed": "शेवटच्या विश्लेषणापासून इनपुट बदलले आहेत",
    "retry": "पुन्हा प्रयत्न करा",
    "error_unreachable": "सर्व्हरशी कनेक्ट होऊ शकले नाही.",
    "error_timeout": "विनंतीची वेळ संपली.",
    "error_server": "सर्व्हर त्रुटी किंवा मॉडेल लोड झाले नाही.",
    "error_invalid_input": "अवैध इनपुट मूल्ये.",
    "error_malformed": "सर्व्हरवरून विकृत डेटा प्राप्त झाला.",
    "analyze": "विश्लेषण करा",
    "loading": "फील्ड डेटाचे विश्लेषण करत आहे...",
    "alternatives": "पर्याय"
  }
};

export const CROP_TRANSLATIONS: Record<string, Record<string, string>> = {
  "apple": {
    "English": "Apple",
    "Hindi": "सेब",
    "Tamil": "ஆப்பிள்",
    "Telugu": "ఆపిల్",
    "Marathi": "सफरचंद"
  },
  "banana": {
    "English": "Banana",
    "Hindi": "केला",
    "Tamil": "வாழைப்பழம்",
    "Telugu": "అరటి",
    "Marathi": "केळी"
  },
  "blackgram": {
    "English": "Blackgram",
    "Hindi": "उड़द",
    "Tamil": "உளுந்து",
    "Telugu": "మినుములు",
    "Marathi": "उडीद"
  },
  "chickpea": {
    "English": "Chickpea",
    "Hindi": "चना",
    "Tamil": "கொண்டைக்கடலை",
    "Telugu": "శనగలు",
    "Marathi": "हरभरा"
  },
  "coconut": {
    "English": "Coconut",
    "Hindi": "नारियल",
    "Tamil": "தேங்காய்",
    "Telugu": "కొబ్బరి",
    "Marathi": "नारळ"
  },
  "coffee": {
    "English": "Coffee",
    "Hindi": "कॉफी",
    "Tamil": "காபி",
    "Telugu": "కాఫీ",
    "Marathi": "कॉफी"
  },
  "cotton": {
    "English": "Cotton",
    "Hindi": "कपास",
    "Tamil": "பருத்தி",
    "Telugu": "పత్తి",
    "Marathi": "कापूस"
  },
  "grapes": {
    "English": "Grapes",
    "Hindi": "अंगूर",
    "Tamil": "திராட்சை",
    "Telugu": "ద్రాక్ష",
    "Marathi": "द्राक्षे"
  },
  "jute": {
    "English": "Jute",
    "Hindi": "जूट",
    "Tamil": "சணல்",
    "Telugu": "జనపనార",
    "Marathi": "ताग"
  },
  "kidneybeans": {
    "English": "Kidney Beans",
    "Hindi": "राजमा",
    "Tamil": "ராஜ்மா",
    "Telugu": "రాజ్మా",
    "Marathi": "राजमा"
  },
  "lentil": {
    "English": "Lentil",
    "Hindi": "मसूर",
    "Tamil": "மைசூர் பருப்பு",
    "Telugu": "ఎర్ర కందిపప్పు",
    "Marathi": "मसूर"
  },
  "maize": {
    "English": "Maize",
    "Hindi": "मक्का",
    "Tamil": "மக்காச்சோளம்",
    "Telugu": "మొక్కజొన్న",
    "Marathi": "मका"
  },
  "mango": {
    "English": "Mango",
    "Hindi": "आम",
    "Tamil": "மாம்பழம்",
    "Telugu": "మామిడి",
    "Marathi": "आंबा"
  },
  "mothbeans": {
    "English": "Moth Beans",
    "Hindi": "मोठ",
    "Tamil": "பயறு",
    "Telugu": "మొలకలు",
    "Marathi": "मठ"
  },
  "mungbean": {
    "English": "Mung Bean",
    "Hindi": "मूंग",
    "Tamil": "பாசிப்பயறு",
    "Telugu": "పెసలు",
    "Marathi": "मूग"
  },
  "muskmelon": {
    "English": "Muskmelon",
    "Hindi": "खरबूजा",
    "Tamil": "முலாம் பழம்",
    "Telugu": "కర్బూజా",
    "Marathi": "खरबूज"
  },
  "orange": {
    "English": "Orange",
    "Hindi": "संतरा",
    "Tamil": "ஆரஞ்சு",
    "Telugu": "నారింజ",
    "Marathi": "संत्रे"
  },
  "papaya": {
    "English": "Papaya",
    "Hindi": "पपीता",
    "Tamil": "பப்பாளி",
    "Telugu": "బొప్పాయి",
    "Marathi": "पपई"
  },
  "pigeonpeas": {
    "English": "Pigeon Peas",
    "Hindi": "अरहर",
    "Tamil": "துவரம் பருப்பு",
    "Telugu": "కందులు",
    "Marathi": "तूर"
  },
  "pomegranate": {
    "English": "Pomegranate",
    "Hindi": "अनार",
    "Tamil": "மாதுளை",
    "Telugu": "దానిమ్మ",
    "Marathi": "डाळिंब"
  },
  "rice": {
    "English": "Rice",
    "Hindi": "चावल",
    "Tamil": "அரிசி",
    "Telugu": "వరి",
    "Marathi": "तांदूळ"
  },
  "watermelon": {
    "English": "Watermelon",
    "Hindi": "तरबूज",
    "Tamil": "தர்பூசணி",
    "Telugu": "పుచ్చకాయ",
    "Marathi": "कलिंगड"
  }
};

export const CONDITION_TRANSLATIONS: Record<string, Record<string, string>> = {
  "Kharif": {
    "English": "Kharif",
    "Hindi": "खरीफ",
    "Tamil": "காரீப்",
    "Telugu": "ఖరీఫ్",
    "Marathi": "खरीप"
  },
  "Rabi": {
    "English": "Rabi",
    "Hindi": "रबी",
    "Tamil": "ராபி",
    "Telugu": "రబీ",
    "Marathi": "रब्बी"
  },
  "Zaid": {
    "English": "Zaid",
    "Hindi": "जायद",
    "Tamil": "சையத்",
    "Telugu": "జైద్",
    "Marathi": "जायद"
  },
  "Perennial": {
    "English": "Perennial",
    "Hindi": "बारहमासी",
    "Tamil": "வற்றாத",
    "Telugu": "బహువార్షిక",
    "Marathi": "बारमाही"
  },
  "Kharif/Rabi": {
    "English": "Kharif/Rabi",
    "Hindi": "खरीफ/रबी",
    "Tamil": "காரீப்/ராபி",
    "Telugu": "ఖరీఫ్/రబీ",
    "Marathi": "खरीप/रब्बी"
  },
  "Kharif/Zaid": {
    "English": "Kharif/Zaid",
    "Hindi": "खरीफ/जायद",
    "Tamil": "காரீப்/சையத்",
    "Telugu": "ఖరీఫ్/జైద్",
    "Marathi": "खरीप/जायद"
  },
  "High": {
    "English": "High",
    "Hindi": "अधिक",
    "Tamil": "அதிக",
    "Telugu": "అధిక",
    "Marathi": "जास्त"
  },
  "Moderate": {
    "English": "Moderate",
    "Hindi": "मध्यम",
    "Tamil": "மிதமான",
    "Telugu": "మధ్యస్థ",
    "Marathi": "मध्यम"
  },
  "Low": {
    "English": "Low",
    "Hindi": "कम",
    "Tamil": "குறைவான",
    "Telugu": "తక్కువ",
    "Marathi": "कमी"
  },
  "Clay/Loam": {
    "English": "Clay/Loam",
    "Hindi": "मिट्टी/दोमट",
    "Tamil": "களிமண்",
    "Telugu": "బంకమట్టి/లోమ్",
    "Marathi": "चिकणमाती/लोम"
  },
  "Loamy": {
    "English": "Loamy",
    "Hindi": "दोमट",
    "Tamil": "களிமண்",
    "Telugu": "లోమ్",
    "Marathi": "लोम"
  },
  "Alluvial": {
    "English": "Alluvial",
    "Hindi": "जलोढ़",
    "Tamil": "வண்டல்",
    "Telugu": "ఒండ్రు",
    "Marathi": "गाळाची"
  },
  "Black Cotton Soil": {
    "English": "Black Cotton Soil",
    "Hindi": "काली कपास मिट्टी",
    "Tamil": "கரிசல் மண்",
    "Telugu": "నల్ల రేగడి",
    "Marathi": "काळी कापूस माती"
  },
  "Sandy Loam": {
    "English": "Sandy Loam",
    "Hindi": "बलुई दोमट",
    "Tamil": "மணல் களிமண்",
    "Telugu": "ఇసుక లోమ్",
    "Marathi": "वाळूयुक्त लोम"
  },
  "Well-drained Loam": {
    "English": "Well-drained Loam",
    "Hindi": "अच्छी जल निकासी वाली दोमट",
    "Tamil": "நன்கு வடிகட்டப்பட்ட களிமண்",
    "Telugu": "బాగా ఎండిపోయిన లోమ్",
    "Marathi": "चांगला निचरा होणारी लोम"
  },
  "Well-drained": {
    "English": "Well-drained",
    "Hindi": "अच्छी जल निकासी वाली",
    "Tamil": "நன்கு வடிகட்டப்பட்ட",
    "Telugu": "బాగా ఎండిపోయిన",
    "Marathi": "चांगला निचरा होणारी"
  },
  "Alluvial/Laterite": {
    "English": "Alluvial/Laterite",
    "Hindi": "जलोढ़/लेटराइट",
    "Tamil": "வண்டல்/லேட்டரைட்",
    "Telugu": "ఒండ్రు/లాటరైట్",
    "Marathi": "गाळाची/लॅटेराइट"
  },
  "Rich Loamy": {
    "English": "Rich Loamy",
    "Hindi": "उपजाऊ दोमट",
    "Tamil": "வளமான களிமண்",
    "Telugu": "సారవంతమైన లోమ్",
    "Marathi": "सुपीक लोम"
  },
  "Clay Loam": {
    "English": "Clay Loam",
    "Hindi": "चिकनी दोमट",
    "Tamil": "களிமண்",
    "Telugu": "బంకమట్టి లోమ్",
    "Marathi": "चिकणमाती लोम"
  },
  "Sandy": {
    "English": "Sandy",
    "Hindi": "बलुई",
    "Tamil": "மணல்",
    "Telugu": "ఇసుక",
    "Marathi": "वाळू"
  },
  "Deep Loam": {
    "English": "Deep Loam",
    "Hindi": "गहरी दोमट",
    "Tamil": "ஆழமான களிமண்",
    "Telugu": "లోతైన లోమ్",
    "Marathi": "खोल लोम"
  },
  "Heavy Clay/Loam": {
    "English": "Heavy Clay/Loam",
    "Hindi": "भारी मिट्टी/दोमट",
    "Tamil": "கனமான களிமண்",
    "Telugu": "బరువైన బంకమట్టి/లోమ్",
    "Marathi": "जड चिकणमाती/लोम"
  },
  "Rich Forest Loam": {
    "English": "Rich Forest Loam",
    "Hindi": "उपजाऊ वन दोमट",
    "Tamil": "வளமான வன களிமண்",
    "Telugu": "సారవంతమైన అటవీ లోమ్",
    "Marathi": "सुपीक जंगल लोम"
  }
};

export function t(lang: SupportedLanguage, key: string): string {
  return TRANSLATIONS[lang]?.[key] || TRANSLATIONS['English']?.[key] || key;
}

export function tCrop(lang: SupportedLanguage, cropName: string): string {
  const c = cropName.toLowerCase();
  return CROP_TRANSLATIONS[c]?.[lang] || CROP_TRANSLATIONS[c]?.['English'] || cropName;
}

export function tCond(lang: SupportedLanguage, cond: string): string {
  if (cond === '-') return cond;
  // Known problem: Tamil words for Loamy, Clay Loam and Clay/Loam are identical.
  return CONDITION_TRANSLATIONS[cond]?.[lang] || CONDITION_TRANSLATIONS[cond]?.['English'] || cond;
}
