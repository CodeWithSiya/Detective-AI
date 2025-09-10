/**
 * ChangePassword Component
 * Provides an interface for a user to change the password of their account
 * 
 * author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 10/09/2025
 */

import React, { useRef, useState } from 'react';
import "./ChangePassword.css";
import { Typewriter } from 'react-simple-typewriter';
import { useNavigate } from 'react-router-dom';
// Import for utility functions for email retrieval and password changing
import { getEmail } from '../ForgotPassword/ForgotPassword';
import { changePassword } from '../AuthHandler';
import {Eye, EyeOff} from 'lucide-react';
/**
 * Function that renders the form for changing password functionality
 * @returns {JSX.Element} ChangePassword Component
 */
const ChangePassword = () => {
    //store references from fields directly
    const passwordRef = useRef();
    const confirmPasswordRef = useRef();

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    //Initialise navigator for navigation between routes
    const navigate = useNavigate();

    /**
     * Function that gets called when submit button is pressed
     * @param {Event} e - the form submission event
     */
    const handleSubmit = (e) => {
        //prevents default behaviour from an event occuring
        e.preventDefault();

        //extract values form the password input fields
        const password = passwordRef.current.value;
        const confirmPassword = confirmPasswordRef.current.value;

        //only change password if passwords match
        if (password === confirmPassword){

            //Mock backend behaviour by attempting to change the password
            const result = changePassword(getEmail(), password);

            alert(result.message); //alert message

            //move to main page when password is changed successfully
            if (result.success){
                navigate("/login");
            }
        }
        else{
            //Error for when passwords don't match
            alert("Passwords do not match");
        }
    };

    
    return (
        <div className="change-container">
            <div className="change-card">
                <h1 className="change-title">
                <Typewriter
                    words={["Change your Password"]}
                    loop={1}
                    cursor
                    cursorStyle="_"
                    typeSpeed={70}
                    deleteSpeed={50}
                    delaySpeed={1000}
                />
                </h1>

                <p className="change-subtitle">Don't forget it this time!</p>

                <form className="change-form" onSubmit={handleSubmit}>
                <div className="form-group" style={{ position: "relative" }}>
                    <label>New Password<span className="required">*</span></label>
                    <input
                    type={showPassword ? "text" : "password"}
                    ref={passwordRef}
                    required
                    style={{ paddingRight: "2.5rem" }}
                    />
                    <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    className="toggle-password"
                    tabIndex={-1}
                    >
                    {showPassword ? <EyeOff className="icon-sm" /> : <Eye className="icon-sm" />}
                    </button>
                </div>

                <div className="form-group" style={{ position: "relative" }}>
                    <label>Confirm Password<span className="required">*</span></label>
                    <input
                    type={showConfirmPassword ? "text" : "password"}
                    ref={confirmPasswordRef}
                    required
                    style={{ paddingRight: "2.5rem" }}
                    />
                    <button
                    type="button"
                    onClick={() => setShowConfirmPassword((prev) => !prev)}
                    className="toggle-password"
                    tabIndex={-1}
                    >
                    {showConfirmPassword ? <EyeOff className="icon-sm" /> : <Eye className="icon-sm" />}
                    </button>
                </div>

                <button type="submit" className="change-button">
                    Submit
                </button>
                </form>
            </div>
        </div>
    );
};

export default ChangePassword