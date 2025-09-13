/** 
 * User Authentication Handler
 * A Authentication handler that performs the required operations via API calls to the backend
 * Updated to use real API endpoints instead of localStorage mock
 * 
 * author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 13/09/2025 
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api'; // Update this to your actual API base URL

// API Helper function for making HTTP requests
async function apiRequest(endpoint, method = 'GET', data = null) {
    try {
        const config = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            config.body = JSON.stringify(data);
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        const result = await response.json();

        if (response.ok) {
            return { success: true, data: result };
        } else {
            return { success: false, message: result.message || 'An error occurred' };
        }
    } catch (error) {
        console.error('API Request Error:', error);
        return { success: false, message: 'Network error. Please try again.' };
    }
}

// COMMENTED OUT: Mock localStorage functions (kept for reference)
/*
/**
 * function that gets all users from localStorage
 * @returns array of users / empty array
 */ 
/*
export function getUsers(){
    return JSON.parse(localStorage.getItem("users")) || [];
}

/**
 * Function that saves the users back into localStorage
 * @param {*} users 
 */
/*
function saveUsers(users){
    localStorage.setItem("users", JSON.stringify(users));
}
*/

/**
 * Function that signs up (registers) a new user via API
 * @param {string} email 
 * @param {string} password 
 * @param {string} firstName
 * @param {string} lastName
 * @param {string} username
 * @return Promise<{success: boolean, message: string, data?: any}>
 */
export async function signUp(email, password, firstName = '', lastName = '', username = '') {
    const userData = {
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        username: username || email.split('@')[0] // Default username from email if not provided
    };

    const result = await apiRequest('/users/register/', 'POST', userData);
    
    if (result.success) {
        return { success: true, message: 'Registration successful! Please check your email to verify your account.' };
    } else {
        return { success: false, message: result.message || 'Registration failed. Please try again.' };
    }
}

// COMMENTED OUT: Mock localStorage signup function (kept for reference)
/*
/**
 * Function that signs up (adds) a new user to localStorage
 * @param {*} email 
 * @param {*} password 
 * @return error object
 */
/*
export function signUp(email, password){
    const users = getUsers() //from localStorage

    //check if email already exists
    if (users.find(user => user.email === email)){
        return {success: false, message: "Email already exists"}
    }

    //no matching email

    users.push({ email, password });  //save users array    
    saveUsers(users); //Store in local Storage

    return {success: true, message: "Signup successful"};

}
*/


/**
 * Function that logs in a user via API
 * @param {string} email 
 * @param {string} password 
 * @returns Promise<{success: boolean, message: string, token?: string, user?: object}>
 */
export async function login(email, password) {
    const loginData = {
        email,
        password
    };

    const result = await apiRequest('/users/login/', 'POST', loginData);
    
    if (result.success) {
        // Store authentication token if provided
        if (result.data.token) {
            localStorage.setItem('authToken', result.data.token);
        }
        // Store user data if provided
        if (result.data.user) {
            localStorage.setItem('userData', JSON.stringify(result.data.user));
        }
        
        return { 
            success: true, 
            message: 'Login successful!',
            token: result.data.token,
            user: result.data.user
        };
    } else {
        return { success: false, message: result.message || 'Invalid email or password' };
    }
}

// COMMENTED OUT: Mock localStorage login function (kept for reference)
/*
/**
 * Function that logs in a user that is in localStorage
 * @param {*} email 
 * @param {*} password 
 * @returns error object
 */
/*
export function login(email, password){
    const users = getUsers();   //From localStorage

    //look for the user in the users array with matching email and password
    const user = users.find(user => user.email === email && user.password === password);

    if (user){
        return {success: true, message: "Login successful"};
    }

    //user doesnt exist
    return {success: false, message: "Invalid email or password" };
}
*/


/**
 * Function that initiates forgot password process via API
 * @param {string} email 
 * @returns Promise<{success: boolean, message: string}>
 */
export async function forgotPassword(email) {
    const forgotPasswordData = { email };

    const result = await apiRequest('/users/forgot-password/', 'POST', forgotPasswordData);
    
    if (result.success) {
        return { success: true, message: 'Password reset link has been sent to your email.' };
    } else {
        return { success: false, message: result.message || 'Email does not exist in our system.' };
    }
}

/**
 * Function that resets/changes the password via API
 * @param {string} token - Reset token from email
 * @param {string} newPassword 
 * @returns Promise<{success: boolean, message: string}>
 */
export async function resetPassword(token, newPassword) {
    const resetData = {
        token,
        new_password: newPassword
    };

    const result = await apiRequest('/users/reset-password/', 'POST', resetData);
    
    if (result.success) {
        return { success: true, message: 'Password reset successful! You can now login with your new password.' };
    } else {
        return { success: false, message: result.message || 'Password reset failed. Please try again.' };
    }
}

/**
 * Function that verifies email with verification code via API
 * @param {string} email 
 * @param {string} verificationCode 
 * @returns Promise<{success: boolean, message: string, token?: string}>
 */
export async function verifyEmail(email, verificationCode) {
    const verifyData = {
        email,
        verification_code: verificationCode
    };

    const result = await apiRequest('/users/verify-email/', 'POST', verifyData);
    
    if (result.success) {
        return { 
            success: true, 
            message: 'Email verified successfully!',
            token: result.data.reset_token // Token for password reset
        };
    } else {
        return { success: false, message: result.message || 'Invalid verification code.' };
    }
}

/**
 * Function that resends verification code via API
 * @param {string} email 
 * @returns Promise<{success: boolean, message: string}>
 */
export async function resendVerification(email) {
    const resendData = { email };

    const result = await apiRequest('/users/resend-verification/', 'POST', resendData);
    
    if (result.success) {
        return { success: true, message: 'Verification code has been resent to your email.' };
    } else {
        return { success: false, message: result.message || 'Failed to resend verification code.' };
    }
}

/**
 * Function that logs out user by clearing stored data
 */
export function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    return { success: true, message: 'Logged out successfully.' };
}

/**
 * Function that checks if user is currently authenticated
 * @returns {boolean}
 */
export function isAuthenticated() {
    return !!localStorage.getItem('authToken');
}

/**
 * Function that gets current user data from localStorage
 * @returns {object|null}
 */
export function getCurrentUser() {
    const userData = localStorage.getItem('userData');
    return userData ? JSON.parse(userData) : null;
}

// COMMENTED OUT: Mock localStorage functions (kept for reference)
/*
/**
 * Function that changes the password of a user
 * @param {*} email 
 * @param {*} newPassword 
 * @returns error object
 */
/*
export function changePassword(email, newPassword){
    const users = getUsers(); //from localStorage

    //find the index of the user in the array
    const index = users.findIndex(user => user.email === email);

    if (index !== -1){
        //user found

        users[index].password = newPassword; //change the users password
        saveUsers(users); //save updated users to localStorage

        return {success: true, message: "Password changed"};
    }

    //user not found
    return { success: false, message: "User not found" };
}

export function emailExists(email){
    const users = getUsers(); //from localStorage

    //look for user
    const user = users.find(user => user.email === email);

    //check if user exists
    if (user){
        return { success: true, message: "User found" };
    }

    return { success: false, message: "Email does not exist" };
}
*/
