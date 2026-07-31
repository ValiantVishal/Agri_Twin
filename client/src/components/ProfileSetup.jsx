import { useState } from "react";
import { useNavigate } from "react-router-dom";
// import "../css/ProfileSetup.css";

function ProfileSetup() {

    const navigate = useNavigate();

    const [form, setForm] = useState({
        phone:"",
        state:"",
        district:"",
        village:"",
        language:"Tamil",
        farmerType:"",
        experience:"",
        crop:"",
        irrigation:"",
        soilType:""
    });

    const handleChange = (e)=>{
        setForm({
            ...form,
            [e.target.name]:e.target.value
        });
    }

    const handleSubmit=(e)=>{
        e.preventDefault();

        console.log(form);

        // API 
        alert("Profile Saved");

        navigate("/dashboard");
    }

    return(
        <div className="container">

            <div className="card">

                <h1>Complete Your Profile</h1>

                <p>Tell us about your farm</p>

                <form onSubmit={handleSubmit}>

                    <input
                        name="phone"
                        placeholder="Phone Number"
                        value={form.phone}
                        onChange={handleChange}
                        required
                    />

                    <input
                        name="state"
                        placeholder="State"
                        value={form.state}
                        onChange={handleChange}
                        required
                    />

                    <input
                        name="district"
                        placeholder="District"
                        value={form.district}
                        onChange={handleChange}
                        required
                    />

                    <input
                        name="village"
                        placeholder="Village"
                        value={form.village}
                        onChange={handleChange}
                        required
                    />

                    <select
                        name="language"
                        value={form.language}
                        onChange={handleChange}
                    >
                        <option>Tamil</option>
                        <option>English</option>
                    </select>

                    <select
                        name="farmerType"
                        value={form.farmerType}
                        onChange={handleChange}
                        required
                    >
                        <option value="">Farmer Type</option>
                        <option>New Farmer</option>
                        <option>Experienced Farmer</option>
                        <option>Retired Farmer</option>
                    </select>

                    <input
                        type="number"
                        name="experience"
                        placeholder="Years of Experience"
                        value={form.experience}
                        onChange={handleChange}
                    />

                    <input
                        name="crop"
                        placeholder="Primary Crop"
                        value={form.crop}
                        onChange={handleChange}
                    />

                    <select
                        name="irrigation"
                        value={form.irrigation}
                        onChange={handleChange}
                    >
                        <option value="">Irrigation Type</option>
                        <option>Canal</option>
                        <option>Borewell</option>
                        <option>Rain-fed</option>
                        <option>Drip</option>
                    </select>

                    <select
                        name="soilType"
                        value={form.soilType}
                        onChange={handleChange}
                    >
                        <option value="">Soil Type</option>
                        <option>Clay</option>
                        <option>Loamy</option>
                        <option>Sandy</option>
                        <option>Red</option>
                        <option>Black</option>
                    </select>

                    <button>
                        Save & Continue
                    </button>

                </form>

            </div>

        </div>
    )

}

export default ProfileSetup;