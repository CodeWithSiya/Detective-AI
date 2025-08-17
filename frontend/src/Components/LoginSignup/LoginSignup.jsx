import React from 'react'
import './LoginSignup.css'

export const LoginSignup = () => {
  return (
    
    <section class="container">
      <form id="my-form">
        <h1>Welcome back</h1>
        <h2>Sign in to continue</h2>
        <div class="msg"></div>
        <div>
          <label for="email">Email:</label>
          <input type="text" id="email"></input>
        </div>
        <div>
          <label for="password">Password:</label>
          <input type="text" id="email"></input>
        </div>
        <input class="btn" type="submit" value="Sign In"></input>
      </form>

    </section>
  )
}
