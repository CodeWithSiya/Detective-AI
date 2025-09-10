/**
 * Signup Component
 * 
 * Provides a user registration interface for creating new accounts.
 * 
 * authors: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 10/09/2025
 * 
 */

import React, { useRef } from 'react';
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

    //Initialise navigator for navigation between routes
    const navigate = useNavigate();

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
                    // Animated typewriter effect for the title
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

                <form>
                    
                </form>
            </div>
        </div>
    );
};

export default Signup