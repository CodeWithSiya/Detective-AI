/**
 * Login Component
 * 
 * Provides a user authentication interface with email and password fields
 * 
 * author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 10/09/2025
 */

import React, { useRef, useState } from 'react';
import "./Login.css";
import { Typewriter } from 'react-simple-typewriter';
import { Link as RouterLink, useNavigate } from "react-router-dom";
import {Eye, EyeOff} from 'lucide-react';
import { login } from '../AuthHandler';

/**
 * Function that renders the main login page.
 */
const Login = () => {
    // Store references for email and password.
    const emailRef = useRef();
    const passwordRef = useRef();

    // Initialise navigation between routes.
    const navigate = useNavigate();

    const [showPassword, setShowPassword] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');

    /**
     * Gets called when submit button is clicked.
     */
    const handleSubmit = async (e) => {
        // Prevent default behaviour.
        e.preventDefault();
        
        // Clear previous error messages.
        setErrorMessage('');
        setIsLoading(true);

        // Extract current values from input fields.
        const email = emailRef.current.value;
        const password = passwordRef.current.value;

        try {
            // API call for user authentication.
            const result = await login(email, password);

            // Move to next page if login successful
            if (result.success) {
                // Store remember me preference if needed
                if (rememberMe) {
                    localStorage.setItem('rememberMe', 'true');
                }
                
                console.log('Login successful:', result.user);
                navigate("/detective");
            } else {
                // Display login error message
                setErrorMessage(result.message || 'Invalid email or password. Please try again.');
            }
        } catch (error) {
            console.error('Login error:', error);
            setErrorMessage('An unexpected error occurred. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                {/* <img src={Logo} alt="Logo" className="login-logo" /> */}

                <h1 className="login-title">
                <Typewriter
                    words={[
                    "Welcome back!",
                    "Let’s get started!",
                    "Case files await!",
                    "Mystery ahead!",
                    "Time to catch AI!"
                    ]}
                    loop
                    cursor
                    cursorStyle="_"
                    typeSpeed={70}
                    deleteSpeed={50}
                    delaySpeed={1000}
                />
                </h1>

                <p className="login-subtitle">Log in to your account</p>

                <form className="login-form" onSubmit={handleSubmit}>
                {errorMessage && (
                    <div style={{ 
                        color: '#ef4444', 
                        backgroundColor: '#fef2f2', 
                        border: '1px solid #fecaca',
                        padding: '0.75rem', 
                        borderRadius: '0.375rem', 
                        marginBottom: '1rem',
                        fontSize: '0.875rem'
                    }}>
                        {errorMessage}
                    </div>
                )}
                
                <div className="form-group">
                    <label>Email<span className="required">*</span></label>
                    <input type="email" placeholder="e.g. me@example.com" ref={emailRef} required />
                </div>

                <div className="form-group" style={{ position: "relative" }}>
                    <label>Password<span className="required">*</span></label>
                    <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    ref={passwordRef}
                    required
                    style={{ paddingRight: "2.5rem" }}
                    />
                    <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    style={{
                        position: "absolute",
                        right: "0.75rem",
                        top: "50%",
                        transform: "translateY(-50%)",
                        background: "none",
                        border: "none",
                        cursor: "pointer",
                        padding: 0
                    }}
                    tabIndex={-1}
                    >
                    {showPassword ? <EyeOff className="icon-sm" /> : <Eye className="icon-sm" />}
                    </button>
                </div>

                <div className="form-extra">
                    <label className="remember-me">
                    <input
                        type="checkbox"
                        checked={rememberMe}
                        onChange={() => setRememberMe((prev) => !prev)}
                    />
                    Remember me
                    </label>
                    <RouterLink to="/forgot-password" className="forgot-password-link">
                    Forgot password?
                    </RouterLink>
                </div>

                <button type="submit" className="login-button" disabled={isLoading}>
                    {isLoading ? 'Logging in...' : 'Log In'}
                </button>

                <p className="login-footer">
                    Don’t have an account?{" "}
                    <RouterLink to="/signup" className="signup-link">
                    Sign up
                    </RouterLink>
                </p>
                </form>
            </div>
        </div>
    );
};

export default Login
