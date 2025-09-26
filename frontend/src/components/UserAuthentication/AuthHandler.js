/** 
 * User Authentication Handler
 * A Authentication handler that performs the required operations via API calls to the backend
 * Updated to use real API endpoints instead of localStorage mock
 * 
 * author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 13/09/2025 
 */

// Base API Configuration.
const API_BASE_URL = 'http://localhost:8000/api'; 

/**
 * Function that signs up (registers) a new user via API with verification.
 */
export async function signUp(email, password, firstName = '', lastName = '', username = '') {
    const userData = {
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        username: username || email.split('@')[0]
    };

    try {
        const response = await fetch(`${API_BASE_URL}/users/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });

        const result = await response.json();

        if (response.ok) {
            // Store user data for verification step.
            localStorage.setItem('pendingVerification', JSON.stringify({
                email: result.data?.email,
                user_id: result.data?.user_id,
                requires_verification: result.data?.requires_verification
            }));

            return {
                success: true,
                message: result.message || 'Registration successful.',
                data: result.data,
                emailSent: result.verification_email?.sent || false,
                emailStatus: result.verification_email?.status || null
            };
        } else {
            return { 
                success: false, 
                message: result.error || result.message || 'Registration failed. Please try again.'
            };
        }
    } catch (error) {
        console.error('Registration Error:', error);
        return { success: false, message: 'Network error. Please try again.' };
    }   
}

/**
 * Function that logs in a user via API
 */
export async function login(email, password) {
    const loginData = { email, password };

    try {
        const response = await fetch(`${API_BASE_URL}/users/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData)
        });

        const result = await response.json();

        if (result.success) {
            // Store authentication token and user data.
            const token = result.data.token;
            const userData = { ...result.data };
            delete userData.token; // Remove token from user data before storing.
            
            localStorage.setItem('authToken', token);
            localStorage.setItem('userData', JSON.stringify(userData));
            localStorage.removeItem('pendingVerification'); // Clear any pending verification.
            
            return { 
                success: true, 
                message: result.message,
                token: token,
                user: userData
            };
        } else {
            // Handle email verification required case
            if (response.status === 403 && result.data?.requires_verification) {
                localStorage.setItem('pendingVerification', JSON.stringify({
                    email: result.data.email,
                    requires_verification: true
                }));
                
                return {
                    success: false,
                    message: result.error,
                    requiresVerification: true,
                    email: result.data.email
                };
            }
            
            return { 
                success: false, 
                message: result.error || 'Invalid email or password'
            };
        }
    } catch (error) {
        console.error('Login Error:', error);
        return { success: false, message: 'Network error. Please try again.' };
    }
}

/**
 * Function that verifies email with verification code.
 */
export async function verifyEmail(email, verificationCode) {
    const verifyData = {
        email,
        verification_code: verificationCode
    };

    try {
        const response = await fetch(`${API_BASE_URL}/users/verify-email/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(verifyData)
        });

        const result = await response.json();

        if (result.success) {
            // Store authentication token and user data
            const token = result.data.token;
            const userData = { ...result.data };
            delete userData.token;
            
            localStorage.setItem('authToken', token);
            localStorage.setItem('userData', JSON.stringify(userData));
            localStorage.removeItem('pendingVerification');
            
            return { 
                success: true, 
                message: result.message,
                token: token,
                user: userData,
                welcomeEmailSent: result.welcome_email?.sent || false
            };
        } else {
            return { 
                success: false, 
                message: result.error || 'Invalid verification code.'
            };
        }
    } catch (error) {
        console.error('Email Verification Error:', error);
        return { success: false, message: 'Network error. Please try again.' };
    }
}

/**
 * Function that resends verification code via API.
 */
export async function resendVerification(email) {
    const resendData = { email };

    try {
        const response = await fetch(`${API_BASE_URL}/users/resend-verification/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(resendData)
        });

        const result = await response.json();

        return {
            success: result.success,
            message: result.message || (result.success ? 'Verification code resent successfully.' : result.error),
            emailSent: result.verification_email?.sent || false,
            emailStatus: result.verification_email?.status
        };
    } catch (error) {
        console.error('Resend Verification Error:', error);
        return { success: false, message: 'Network error. Please try again.' };
    }
}

/**
 * Function that initiates forgot password process via API.
 */
export async function forgotPassword(email) {
    const forgotPasswordData = { email };

    try {
        const response = await fetch(`${API_BASE_URL}/users/forgot-password/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(forgotPasswordData)
        });

        const result = await response.json();

        return { 
            success: result.success,
            message: result.message || (result.success ? 'Password reset link sent.' : result.error),
            emailSent: result.password_reset_email?.sent || false,
            emailStatus: result.password_reset_email?.status
        };
    } catch (error) {
        console.error('Forgot Password Error:', error);
        return { success: false, message: 'Network error. Please try again.' };
    }
}

/**
 * Function that resets/changes the password via API
 * @param {string} token - Reset token from email
 * @param {string} newPassword 
 * @returns Promise<{success: boolean, message: string}>
 */
export async function resetPassword(uid, token, newPassword, confirmPassword) {
    const resetData = {
        uid,
        token,
        new_password: newPassword,
        confirm_password: confirmPassword
    };

    try {
        const response = await fetch(`${API_BASE_URL}/users/reset-password/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(resetData)
        });

        const result = await response.json();

        return { 
            success: result.success, 
            message: result.message || (result.success ? 'Password reset successful!' : result.error)
        };
    } catch (error) {
        console.error('Reset Password Error:', error);
        return { success: false, message: 'Network error. Please try again.' };
    }
}

/**
 * Function that changes user password via API
 */
export async function changePassword(userId, currentPassword, newPassword, confirmPassword) {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
        return { success: false, message: 'Not authenticated' };
    }
    
    const changeData = {
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword
    };

    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/change-password/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}`
            },
            body: JSON.stringify(changeData)
        });

        const result = await response.json();

        return {
            success: result.success,
            message: result.message || (result.success ? 'Password changed successfully.' : result.error)
        };
    } catch (error) {
        console.error('Change Password Error:', error);
        return { success: false, message: 'Network error. Please try again.' };
    }
}

/**
 * Function that gets current user profile via API
 */
export async function getCurrentUserProfile() {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
        return { success: false, message: 'Not authenticated' };
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/me/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}`
            }
        });

        const result = await response.json();

        if (result.success) {
            // Update stored user data
            localStorage.setItem('userData', JSON.stringify(result.data));
            
            return {
                success: true,
                user: result.data
            };
        }
        
        // If token is invalid, clear local storage
        if (response.status === 401) {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userData');
        }
        
        return {
            success: false,
            message: result.error || 'Failed to get user data'
        };
    } catch (error) {
        console.error('Get User Profile Error:', error);
        return { success: false, message: 'Network error. Please try again.' };
    }
}

/**
 * Function that updates user profile via API
 */
export async function updateUserProfile(userId, updateData) {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
        return { success: false, message: 'Not authenticated' };
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/update/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}`
            },
            body: JSON.stringify(updateData)
        });

        const result = await response.json();

        if (result.success) {
            // Update stored user data
            localStorage.setItem('userData', JSON.stringify(result.data));
            
            return {
                success: true,
                message: result.message,
                user: result.data
            };
        }
        
        return {
            success: false,
            message: result.error || 'Failed to update profile'
        };
    } catch (error) {
        console.error('Update Profile Error:', error);
        return { success: false, message: 'Network error. Please try again.' };
    }
}
 
/**
 * Function that clears stored data.
 */
export async function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    localStorage.removeItem('pendingVerification');
    return { success: true, message: 'Logged out successfully.' };
}

/**
 * Function that deletes user account via API.
 */
export async function deleteUserAccount(userId) {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
        return { success: false, message: 'Not authenticated' };
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/delete/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}`
            }
        });

        const result = await response.json();

        if (result.success) {
            // Clear local storage after successful deletion
            localStorage.removeItem('authToken');
            localStorage.removeItem('userData');
            localStorage.removeItem('pendingVerification');
        }
        
        return {
            success: result.success,
            message: result.message || (result.success ? 'Account deleted successfully.' : result.error)
        };
    } catch (error) {
        console.error('Delete Account Error:', error);
        return { success: false, message: 'Network error. Please try again.' };
    }
}

/**
 * Function that checks if user is currently authenticated
 * @returns {boolean}
 */
export function isAuthenticated() {
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('userData');
    return !!(token && userData);
}

/**
 * Function that gets current user data from localStorage
 * @returns {object|null}
 */
export function getCurrentUser() {
    try {
        const userData = localStorage.getItem('userData');
        return userData ? JSON.parse(userData) : null;
    } catch (error) {
        console.error('Error parsing stored user data:', error);
        return null;
    }
}

/**
 * Function that gets auth token from localStorage
 */
export function getAuthToken() {
    return localStorage.getItem('authToken');
}

/**
 * Function that gets pending verification data from localStorage
 */
export function getPendingVerification() {
    try {
        const pending = localStorage.getItem('pendingVerification');
        return pending ? JSON.parse(pending) : null;
    } catch (error) {
        console.error('Error parsing pending verification data:', error);
        return null;
    }
}