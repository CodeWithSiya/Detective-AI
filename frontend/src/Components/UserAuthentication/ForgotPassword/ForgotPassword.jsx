/**
 * Forgot Password Component
 * 
 * Provides an interface for users to initiate password reset by entering their email
 * 
 * author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 10/09/2025
 */


import React, { useRef } from 'react';
import "./ForgotPassword.css";
import { Typewriter } from 'react-simple-typewriter';
import { useNavigate } from 'react-router-dom';
// Import authentication handler for email verification
import { emailExists } from '../AuthHandler';

let emailValue = null;

/**
 * Function that sets the email for the password reset
 * @param {string} email 
 */
export const setEmail = (email) => {
  emailValue = email;
};

/**
 * Function that gets the email value for the password reset
 * @returns {string|null}
 */
export const getEmail = () => {
  return emailValue;
};

/**
 * Function that renders the form for forgot password component
 * @returns {JSX.Element} ForgotPasswordComponent
 */
const ForgotPassword = () => {
    //Initialise navigator for navigating between routes
    const navigate = useNavigate();

    //Create ref to access email input field
    const emailRef = useRef();

    /**
     * Function gets called when the submit button gets pressed
     * @param {Event} e 
     */
    const handleSubmit = (e) => {
        //prevents default submission behaviour
        e.preventDefault();

        // Check if the entered email exists in the sytem
        const result = emailExists(emailRef.current.value);

        if (result.success){
            //If found
            setEmail(emailRef.current.value);

            navigate('/verify-email');
        }
        else{
            //Error message if not found/invalid
            alert(result.message);
        }
    }

    return (
        
    );
};
export default ForgotPassword;


