/**
 * Signup Component
 * 
 * Provides a user registration interface for creating new accounts.
 * 
 * authors: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 10/09/2025
 * 
 */

import React, { useRef, useState } from 'react';
import "./Signup.css";
import Logo from '../../Assets/Logo.jpg';
import { Typewriter } from 'react-simple-typewriter';
import { useNavigate, Link as RouterLink } from 'react-router-dom';

// Import authentication handler for user registration
import { signUp } from '../AuthHandler';

/**
 * function that renders the registration form 
 * @returns {JSX.Element} Signup Component
 */
const Signup = () => {
    //Access field values
    const nameRef = useRef();
    const emailRef = useRef();
    const passwordRef = useRef();
    const confirmPasswordRef = useRef();
    const lastNameRef = useRef();

    const [passwordStrength, setPasswordStrength] = useState(0);

    //Initialise navigator for navigation between routes
    const navigate = useNavigate();

    const handlePasswordChange = (e) => {
        const value = e.target.value;
        passwordRef.current.value = value;

        // Simple strength calculation
        let strength = 0;
        if (value.length > 6) strength += 25;
        if (/[A-Z]/.text(value)) strength += 25;
        if (/[0-9]/.test(value)) strength += 25;
        if (/[^A-Za-z0-9]/.test(value)) strength += 25;

        setPasswordStrength(strength);
    };

    /**
     * Handles form submission when the "Sign up" button is clicked
     * @param {Event} e 
     */
    const handleSubmit = (e) => {
        // Prevents default submit behaviour
        e.preventDefault();

        //Extract current values from fields
        const firstName = nameRef.current.value;
        const lastName = lastNameRef.current.value;
        const email = emailRef.current.value;
        const password = passwordRef.current.value;
        const confirmPassword = confirmPasswordRef.current.value;

        //Validate password
        if (password === confirmPassword){

            //Attempt to create a new user
            const result = signUp(email, password);

            //Display result message to user
            alert(result.message)

            // If success, navigate to main page
            if (result.success){
                navigate("/login")
            }
        }
        else{
            //Error
            alert("Passwords do not match");
        }
    };

    return (
        // Main container
        <div className="signup-container">
            <div className="signup-card">
                <img src={Logo} alt="Logo" className="signup-logo" />
                
                <h1 className="signup-title">
                    <Typewriter
                        words={["Become a Detective!"]}
                        loop={1}
                        cursor
                        cursorStyle='_'
                        typeSpeed={70}
                        deleteSpeed={50}
                        delaySpeed={1000}
                    />
                </h1>

                <p className="signup-subtitle">Create your account </p>

                <form className="signup-form" onSubmit={handleSubmit}>
                    <div className="form-row">

                        <div className="form-group">
                            <label>First Name<span className="required">*</span></label>
                            <input type="text" placeholder="e.g. Peter" ref={nameRef} required/>
                        </div>

                        <div className="form-group">
                            <label>Last Name</label>
                            <input type="text" placeholder="e.g. Parker" ref={lastNameRef}/>
                        </div>
                    </div>
                        
                    <div className="form-group">
                        <label>Email<span className="required">*</span></label>
                        <input type="email" placeholder="e.g. peter.parker@example.com" ref={emailRef} required/>
                    </div>

                    <div className="form-group">
                        <label>Password<span className="required">*</span></label>
                        <input type="password" onChange={handlePasswordChange} required/>
                        {/* Password Strength Indicator */}
                        <div className="password-strength-bar">
                            <div
                                className={`password-strength-fill ${
                                    passwordStrength < 50
                                        ? "weak"
                                        : passwordStrength < 75
                                        ? "medium"
                                        : "strong"
                                }`}
                                style={{ width: `${passwordStrength}%` }}
                            ></div>
                        </div>
                        <p className="password-strength-label">
                            {passwordStrength === 0
                                ? "Enter a password"
                                : passwordStrength < 50
                                ? "Weak"
                                : passwordStrength < 75
                                ? "Medium"
                                : "Strong"
                            }
                        </p>
                    </div>

                    <div className="form-group">
                        <label>Confirm Password<span className="required">*</span></label>
                        <input type="password" ref={confirmPasswordRef} required/>
                    </div>

                    <button type="submit" className="signup-button">
                        Sign up
                    </button>

                    <p className="signup-footer">
                        Already a user?{" "}
                        <RouterLink to="/login" className="login-link">
                            Log in
                        </RouterLink>
                    </p>
                </form>
            </div>
        </div>
    );
};

export default Signup