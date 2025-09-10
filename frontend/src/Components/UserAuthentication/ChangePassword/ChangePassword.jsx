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
        
    );
};

export default ChangePassword