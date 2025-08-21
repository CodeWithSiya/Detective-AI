// A Authentication handler that performs the required operations on the user data on LocalStorage. (mocks backend)

/**
 * function that gets all users from localStorage
 * @returns array of users / empty array
 */ 
export function getUsers(){
    return JSON.parse(localStorage.getItem("users")) || [];
}

/**
 * Function that saves the users back into localStorage
 * @param {*} users 
 */
function saveUsers(users){
    localStorage.setItem("users", JSON.stringify(users));
}

/**
 * Function that signs up (adds) a new user to localStorage
 * @param {*} email 
 * @param {*} password 
 * @return error object
 */
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


/**
 * Function that logs in a user that is in localStorage
 * @param {*} email 
 * @param {*} password 
 * @returns error object
 */
export function login(email, password){
    const users = getUsers();   //From localStorage

    //look for the user in the users array with matching email and password
    const user = users.find(user => user.email === email && user.password === password);

    if (user){
        //if found save user as currentUser in localStorage
        localStorage.setItem("currentUser", JSON.stringify(user));
        return {success: true, message: "Login successful"};
    }

    //user doesnt exist
    return {success: false, message: "Invalid email or password" };
}


/**
 * Function that changes the password of a user
 * @param {*} email 
 * @param {*} newPassword 
 * @returns error object
 */
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



