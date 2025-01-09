LANGUAGE_CATEGORIES = {
    "Major World Languages": {
        "arabic": "Arabic",
        "bengali": "Bengali",
        "chinese": "Chinese (Mandarin)",
        "cantonese": "Chinese (Cantonese)",
        "english": "English",
        "french": "French",
        "german": "German",
        "hindi": "Hindi",
        "indonesian": "Indonesian",
        "italian": "Italian",
        "japanese": "Japanese",
        "korean": "Korean",
        "persian": "Farsi",
        "portuguese": "Portuguese",
        "russian": "Russian",
        "spanish": "Spanish",
        "turkish": "Turkish",
        "urdu": "Urdu",
        "vietnamese": "Vietnamese"
    },
    "African Languages": {
        "amharic": "Amharic",        # Ethiopia
        "hausa": "Hausa",            # Nigeria, Niger, Ghana
        "igbo": "Igbo",              # Nigeria
        "lingala": "Lingala",        # Congo Basin
        "oromo": "Oromo",            # Ethiopia, Kenya
        "somali": "Somali",          # Somalia, Ethiopia
        "swahili": "Swahili",        # East Africa
        "twi": "Twi",                # Ghana
        "wolof": "Wolof",            # Senegal, Gambia
        "yoruba": "Yoruba",          # Nigeria, Benin
        "zulu": "Zulu",              # South Africa
        "bambara": "Bambara",        # Mali
        "bemba": "Bemba",            # Zambia
        "chichewa": "Chichewa",      # Malawi
        "ganda": "Ganda",            # Uganda
        "kikuyu": "Kikuyu",          # Kenya
        "kinyarwanda": "Kinyarwanda", # Rwanda
        "luganda": "Luganda",        # Uganda
        "luo": "Luo",                # Kenya
        "makonde": "Makonde",        # Tanzania
        "ndebele": "Ndebele",        # Zimbabwe
        "nyanja": "Nyanja",          # Malawi
        "shona": "Shona",            # Zimbabwe
        "swati": "Swati",            # Swaziland
        "tswana": "Tswana",          # Botswana
        "venda": "Venda",            # South Africa
        "xhosa": "Xhosa"             # South Africa
    },
    "European Languages": {
        "albanian": "Albanian",
        "armenian": "Armenian",
        "azerbaijani": "Azerbaijani",
        "belarusian": "Belarusian",
        "bosnian": "Bosnian",
        "bulgarian": "Bulgarian",
        "croatian": "Croatian",
        "czech": "Czech",
        "danish": "Danish",
        "dutch": "Dutch",
        "estonian": "Estonian",
        "finnish": "Finnish",
        "greek": "Greek",
        "hungarian": "Hungarian",
        "icelandic": "Icelandic",
        "irish": "Irish",
        "latvian": "Latvian",
        "lithuanian": "Lithuanian",
        "macedonian": "Macedonian",
        "maltese": "Maltese",
        "moldovan": "Moldovan",
        "montenegrin": "Montenegrin",
        "norwegian": "Norwegian",
        "polish": "Polish",
        "romanian": "Romanian",
        "serbian": "Serbian",
        "slovak": "Slovak",
        "slovenian": "Slovenian",
        "swedish": "Swedish",
        "ukrainian": "Ukrainian"
    },
    "Asian Languages": {
        "burmese": "Burmese",
        "gujarati": "Gujarati",
        "khmer": "Khmer",
        "lao": "Lao",
        "malay": "Malay",
        "punjabi": "Punjabi",
        "tamil": "Tamil",
        "telugu": "Telugu",
        "thai": "Thai",
        "tibetan": "Tibetan"
    },
    "Middle Eastern Languages": {
        "hebrew": "Hebrew",
        "kurdish": "Kurdish",
        "pashto": "Pashto",
        "syriac": "Syriac"
    },
    "Indigenous American Languages": {
        "apache": "Apache",
        "chamorro": "Chamorro",
        "cherokee": "Cherokee",
        "chickasaw": "Chickasaw",
        "choctaw": "Choctaw",
        "comanche": "Comanche",
        "cree": "Cree",
        "haida": "Haida",
        "haudenosaunee": "Haudenosaunee",
        "inuit": "Inuit",
        "iroquois": "Iroquois",
        "kiowa": "Kiowa",
        "lakota": "Lakota",
        "maya": "Maya",
        "navajo": "Navajo",
        "pueblo": "Pueblo",
        "quechua": "Quechua",
        "tlingit": "Tlingit",
        "yaqui": "Yaqui",
        "zuni": "Zuni"
    },
    "Pacific Languages": {
        "fijian": "Fijian",
        "hawaiian": "Hawaiian",
        "maori": "Maori",
        "samoan": "Samoan",
        "tagalog": "Tagalog",
        "tahitian": "Tahitian",
        "tongan": "Tongan"
    }
}

# Create a flat dictionary of all available languages for quick lookup
AVAILABLE_LANGUAGES = {}
for category in LANGUAGE_CATEGORIES.values():
    AVAILABLE_LANGUAGES.update(category)
