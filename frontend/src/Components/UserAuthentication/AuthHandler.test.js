/**
 * Jest unit testing for the AuthHandler.js
 */

const { signUp, login, getUsers, changePassword } = require("./AuthHandler.js");


// run before each individual test
beforeEach( () => {
    let store = {}; //simulate an empty localStorage

    //mock local storage
    global.localStorage = {
        getItem: (key) => store[key] || null, //return value or null
        setItem: (key, value) => {store[key] = String(value);}, //Store value as a string
        removeItem: (key) => {delete store[key];}, //delete item in storage
        clear: () => { store = {}; } //empties entire storage
    };

    localStorage.clear(); //clear mocked localStorage before each run
});

test("Signup function should add a new user correctly", () => {
    const result = signUp("test@example.com", "1234");
    expect(result.success).toBe(true);

    const users = getUsers();
    expect(users).toHaveLength(1);
    expect(users[0].email).toBe("test@example.com")
});

test("Signup function should fail if email exists already", () => {
  signUp("test@example.com", "1234");
  const result = signUp("test@example.com", "abcd");

  expect(result.success).toBe(false);
  expect(result.message).toBe("Email already exists");
});

test("Login should work with correct credentials", () => {
  signUp("user@example.com", "password");
  const result = login("user@example.com", "password");

  expect(result.success).toBe(true);
});

test("Login should fail with incorrect password", () => {
  signUp("user@example.com", "password");
  const result = login("user@example.com", "wrongPassword");

  expect(result.success).toBe(false);
  expect(result.message).toBe("Invalid email or password");
});

test("changePassword should update the user password", () => {
  signUp("user@example.com", "password");
  changePassword("user@example.com", "newpassword");

  const result = login("user@example.com", "newpassword");
  expect(result.success).toBe(true);
});


