/**
 * Signup Component
 * 
 * Provides a user registration interface for creating new accounts.
 * 
 * authors: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 22/08/2025
 * 
 */

import React, { useRef } from 'react';
import { FormControl } from '@chakra-ui/form-control';
import { motion } from 'framer-motion'
import { Typewriter } from 'react-simple-typewriter';
import { Link as RouterLink } from "react-router-dom";
import { useNavigate } from 'react-router-dom';

// Import authentication handler for user registration
import { signUp } from './AuthHandler';

// Custom password input components with built-in functionality
import {
  PasswordInput,
  PasswordStrengthMeter,
} from "@/components/ui/password-input"

// Chakra UI components for styling and layout
import {
  Box,
  Flex,
  Heading,
  Image,
  Input,
  Button,
  Text,
  Link,
  Stack,
  HStack,
  Field,
} from "@chakra-ui/react";


/**
 * function that renders the registration form 
 * @returns {JSX.Element} Signup Component
 */
const Signup = () => {

    //Initialise motion box for animation
    const MotionBox = motion(Box);

    //Access field values
    const nameRef = useRef();
    const emailRef = useRef();
    const passwordRef = useRef();
    const confirmPasswordRef = useRef();
    const lastNameRef = useRef();

    //Initialise navigator for navigation between routes
    const navigate = useNavigate();


    /**
     * Handles form submission when the "Sign up" button is clicked
     * @param {Event} e 
     */
    const handleSubmit = (e) => {
        // Prevents default submit behaviour
        e.preventDefault();

        //Extract current values from fields
        const firstName = nameRef.current.value;
        const lastName = lastNameRef.current.value;
        const email = emailRef.current.value;
        const password = passwordRef.current.value;
        const confirmPassword = confirmPasswordRef.current.value;

        //Validate password
        if (password === confirmPassword){

            //Attempt to create a new user
            const result = signUp(email, password);

            //Display result message to user
            alert(result.message)

            // If success, navigate to main page
            if (result.success){
                navigate("/detective")
            }

        }
        else{
            //Error
            alert("Passwords do not match");
        }
    }

    return (
        //Main container
        <Flex
            minH={'100vh'} //take full height
            align={'center'} //vertically center
            justify={'center'} //horizontal center
        >
            {/* Main content stack */}
            <Stack 
                spacing={8} //space between stacked children
                mx={'auto'} //Centre stack horizontally
                maxW={'lg'} //Max width
                py={12} // p-top and p-bottonm
                px={6} // p-left and p-right
            >
                {/* Header section */}
                <Stack align={'center'}>
                    {/* Logo */}
                    <Image src="/src/Components/Assets/Logo.jpg" alt="Logo" boxSize="250px" mb={4} />

                    {/* Heading with typewriter animation */}
                    <Heading fontSize={'4xl'} color={"black"}>
                        <Typewriter
                            words={['Become a Detective!',]}
                            loop={1}
                            cursor
                            cursorStyle="_"
                            typeSpeed={70}
                            deleteSpeed={50}
                            delaySpeed={1000}
                        />
                    </Heading>

                    {/* Subtitle */}
                    <Text fontSize={'lg'} color={'gray.600'}>
                        Create an account to continue
                    </Text>
                </Stack>

                {/* Signup form with animation */}
                <MotionBox

                    rounded={'lg'} //rounded corners
                    bg={"white"}
                    boxShadow={'lg'} //Shadow-effect behind card
                    p={8} //padding
                    w="500px"

                    //Animate box
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                >
                    <Stack spacing={4}>
                    
                        <HStack>
                            <Box flex={1}>

                                {/* Name field */}
                                <FormControl id="firstName">
                                    <Field.Root required>
                                        <Field.Label>Name<Field.RequiredIndicator /></Field.Label>
                                            <Input placeholder="e.g. John" ref={nameRef} />
                                    </Field.Root>
                                </FormControl>
                            </Box>

                            <Box flex={1}> 
                                
                                {/* last name field */}
                                <FormControl id="lastName">
                                    <Field.Root>
                                        <Field.Label>Last Name</Field.Label>
                                            <Input placeholder="e.g. Doe" ref={lastNameRef} />
                                    </Field.Root>
                                </FormControl>
                            </Box>
                        </HStack>

                        {/* email field */}
                        <FormControl id="email">
                            <Field.Root required>
                                <Field.Label>Email<Field.RequiredIndicator /></Field.Label>
                                    <Input placeholder="johndoe@example.com" ref={emailRef}/>
                            </Field.Root>
                        </FormControl>

                        {/* password field */}
                        <FormControl id="password" isRequired>
                            <Stack>
                                <Field.Root required>
                                    <Field.Label>Password<Field.RequiredIndicator /></Field.Label>
                                        <PasswordInput ref={passwordRef}/>
                                </Field.Root>
                                <PasswordStrengthMeter value={2} />
                            </Stack>
                        </FormControl>
                        
                        {/* confirm password field */}
                        <FormControl id="confirm-password">
                            <Stack>
                                <Field.Root required>
                                    <Field.Label>Confirm Password<Field.RequiredIndicator /></Field.Label>
                                        <PasswordInput ref={confirmPasswordRef}/>
                                </Field.Root>
                            </Stack>
                        </FormControl>

                        {/* sign up button */}
                        <Button
                            bg={'black'}
                            variant={'solid'}
                            color={'white'}
                            _hover={{
                            bg: 'blackAlpha.800',
                            }}
                            onClick={handleSubmit}
                        >
                            Sign up
                        </Button>
                        
                        {/* log in link */}
                        <Text textAlign="center">
                                Already a user?{" "}
                            <Link 
                                as={RouterLink} 
                                _hover={{ color: "gray.500" }} 
                                to="/login" color="black" 
                            >
                                Log in
                            </Link>
                        </Text>

                    </Stack>
                    
                </MotionBox>
            </Stack>

        </Flex>
    )
}

export default Signup