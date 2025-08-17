import React, { useState } from 'react';
import './LoginSignup.css';

export const LoginSignup = () => {

    //Update state as user inputs
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [rememberMe, setRememberMe] = useState('');



    const handleSubmit = (e) => {
        //Prevent default submit behaviour
        e.preventDefault();

        //Log values to console
        console.log("Email:", email);
        console.log("Password:", password);
    };


    const handleGoogleLogin = () => {

    }

    const handleGithubLogin = () => {

    }

    const handleFacebookLogin = () => {
        
    }

    return (
        <section className="container">
            <div className="form-wrapper">

                {/* Left side: Image */}
                <div className="image-side">
                    <img src="/path-to-your-image.jpg" alt="Login illustration" />
                </div>

                <form id="my-form" onSubmit={handleSubmit}>

                    

                    {/* Header */}
                    <h1>Welcome back</h1>
                    <h2>Sign in to continue</h2>
                    <div className="msg"></div>

                    {/* Email field */}
                    <div>
                    <label>Email:</label>
                    <input 
                        type="email" 
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                    </div>

                    {/* Password field*/}
                    <div>
                    <label>Password:</label>
                    <input 
                        type="password" 
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    </div>
                    {/* Remember me checkbox and forgot password*/}
                    <div>
                        <label>
                            <input 
                                type="checkbox" 
                                checked={rememberMe}
                                onChange={(e) => setRememberMe(e.target.checked)}
                            />
                            Remember me
                        </label>

                        <a href="/forgot-password">Forgot password?</a>
                    </div>



                    <button type='button'>Login</button>

                    {/* Divider */}
                    <div>
                        <span>or sign in with</span>
                    </div>

                    {/* Third-party sign in buttons*/}
                    <div>
                        <button type="button" onClick={handleGoogleLogin}>Google</button>
                        <button type="button" onClick={handleGithubLogin}>GitHub</button>
                        <button type="button" onClick={handleFacebookLogin}>Facebook</button>
                    </div>

                    {/* Sign up link */}
                    <div>
                        <p>
                            Don't have an account? <a href="/signup">Sign up</a>
                        </p>
                    </div>

                </form>
            </div>
        </section>
    );
};
