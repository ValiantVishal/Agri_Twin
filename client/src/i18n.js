import i18n from "i18next";
import { initReactI18next } from "react-i18next";

const resources = {
  English: {
    translation: {
      "title": "Field Plot Mapping",
      "back_to_dashboard": "Back to Dashboard",
      "start_walk": "Start Walk Tracking",
      "stop_walk": "Pause Tracking",
      "drop_pin": "Drop Pin Here",
      "close_plot": "Close Plot boundary",
      "save_plot": "Save Plot to Cloud",
      "reset": "Clear Map",
      "plot_name_placeholder": "Enter Plot Name (e.g., North Rice Field)",
      "area": "Calculated Area",
      "perimeter": "Perimeter",
      "accuracy": "GPS Accuracy",
      "status": "Sync Status",
      "synced": "Synced",
      "unsynced": "Offline (Unsynced)",
      "saved_plots": "Your Saved Plots",
      "no_plots": "No plots recorded yet. Go out and walk your field boundary!",
      "accuracy_warning": "Warning: GPS accuracy is weak (> 10m). Try moving to an open area under the sky.",
      "min_points_warning": "You need to capture at least 3 points to close the plot boundary.",
      "self_intersecting_warning": "Warning: The boundary line crosses itself. Please adjust or delete intersecting points.",
      "success_save": "Plot saved successfully!",
      "offline_save": "Offline: Saved locally. Plot will sync automatically when your internet returns.",
      "syncing_now": "Syncing offline plots...",
      "recenter": "Recenter on Me",
      "nudge_instruction": "Nudge Coordinate (Enter new Lat/Lng):",
      "delete_point": "Delete Point",
      "nudge_point": "Nudge Point",
      "confirm_delete_plot": "Are you sure you want to delete this plot?",
      "meters": "meters",
      "acres": "Acres",
      "cents": "Cents",
      "save_btn": "Save",
      "cancel_btn": "Cancel",
      "edit_plot": "Re-map / Edit",
      "remapping_mode": "Re-mapping Mode (Click save to update)",
      "gps_unsupported": "Geolocation is not supported by your browser.",
      "gps_permission_denied": "GPS access was denied. Please enable location permissions in your browser settings and refresh.",
      "server_warning": "Server Notice: "
    }
  },
  Tamil: {
    translation: {
      "title": "நில வரைபடம் (வரைபடம்)",
      "back_to_dashboard": "முகப்புப் பக்கத்திற்குச் செல்",
      "start_walk": "பதிவு செய்யத் தொடங்கு",
      "stop_walk": "பதிவை நிறுத்து",
      "drop_pin": "இங்கே புள்ளியை வை",
      "close_plot": "எல்லையை மூடு",
      "save_plot": "வரைபடத்தை சேமி",
      "reset": "வரைபடத்தை அழி",
      "plot_name_placeholder": "நிலத்தின் பெயர் (உதாரணம்: வடக்கு நெல் வயல்)",
      "area": "கணக்கிடப்பட்ட பரப்பளவு",
      "perimeter": "சுற்றளவு",
      "accuracy": "ஜி.பி.எஸ் துல்லியம்",
      "status": "ஒத்திசைவு நிலை",
      "synced": "சேமிக்கப்பட்டது",
      "unsynced": "ஆஃப்லைன் (ஒத்திசைக்கப்படவில்லை)",
      "saved_plots": "உங்கள் நில வரைபடங்கள்",
      "no_plots": "இன்னும் வரைபடங்கள் இல்லை. உங்கள் நில எல்லையில் நடந்து பதிவு செய்யவும்!",
      "accuracy_warning": "எச்சரிக்கை: ஜி.பி.எஸ் துல்லியம் குறைவாக உள்ளது (> 10 மீ). திறந்த வெளிக்குச் செல்லவும்.",
      "min_points_warning": "எல்லையை மூட குறைந்தபட்சம் 3 புள்ளிகள் தேவை.",
      "self_intersecting_warning": "எச்சரிக்கை: எல்லைக் கோடு ஒன்றையொன்று வெட்டுகிறது. புள்ளிகளைச் சரிசெய்யவும்.",
      "success_save": "நில வரைபடம் வெற்றிகரமாகச் சேமிக்கப்பட்டது!",
      "offline_save": "ஆஃப்லைன்: கணினியில் சேமிக்கப்பட்டது. இணையம் வந்ததும் தானாகவே பதிவேற்றப்படும்.",
      "syncing_now": "ஆஃப்லைன் வரைபடங்கள் பதிவேற்றப்படுகின்றன...",
      "recenter": "எனது இடத்தை மையப்படுத்து",
      "nudge_instruction": "புள்ளியை மாற்று (புதிய அட்சரேகை/தீர்க்கரேகை உள்ளிடவும்):",
      "delete_point": "புள்ளியை நீக்கு",
      "nudge_point": "புள்ளியை நகர்த்து",
      "confirm_delete_plot": "இந்த வரைபடத்தை நீக்க விரும்புகிறீர்களா?",
      "meters": "மீட்டர்",
      "acres": "ஏக்கர்",
      "cents": "சென்ட்",
      "save_btn": "சேமி",
      "cancel_btn": "ரத்துசெய்",
      "edit_plot": "மாற்றியமை / திருத்து",
      "remapping_mode": "மாற்றியமைக்கும் முறை (புதுப்பிக்க சேமிக்கவும்)",
      "gps_unsupported": "உங்கள் உலாவியில் ஜி.பி.எஸ் வசதி இல்லை.",
      "gps_permission_denied": "ஜி.பி.எஸ் அனுமதி மறுக்கப்பட்டது. உலாவியின் அமைப்புகளில் அனுமதியை வழங்கிவிட்டு புதுப்பிக்கவும்.",
      "server_warning": "சேவையக அறிவிப்பு: "
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: "English",
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
