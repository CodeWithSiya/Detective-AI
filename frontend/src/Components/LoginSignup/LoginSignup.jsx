import React, { useState } from 'react';
import './LoginSignup.css';

export const LoginSignup = () => {

    //Update state as user inputs
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');


    const handleSubmit = (e) => {
        //Prevent default submit behaviour
        e.preventDefault();

        //Log values to console
        console.log("Email:", email);
        console.log("Password:", password);
    };

    return (
        <section className="container">
        <form id="my-form" onSubmit={handleSubmit}>
            <h1>Welcome back</h1>
            <h2>Sign in to continue</h2>
            <div className="msg"></div>

            <div>
            <label>Email:</label>
            <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
            />
            </div>

            <div>
            <label>Password:</label>
            <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            </div>

            <input className="btn" type="submit" value="Login" />
        </form>
        </section>
    );
};
