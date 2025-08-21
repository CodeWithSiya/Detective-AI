/**
 * ChangePassword Component
 * Provides an interface for a user to change the password of their account
 * 
 * author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 22/08/2025
 */

import React, { useRef } from 'react';
import { FormControl } from '@chakra-ui/form-control';
import { motion } from 'framer-motion'
import { Typewriter } from 'react-simple-typewriter';
import { useNavigate } from 'react-router-dom';

//Custom password input components with built-in functionality
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
  Button,
  Text,
  Stack,
  Field,
} from "@chakra-ui/react";

// Import for utility functions for email retrieval and password changing
import { getEmail } from './ForgotPassword';
import { changePassword } from './AuthHandler';

/**
 * Function that renders the form for changing password functionality
 * @returns {JSX.Element} ChangePassword Component
 */
const ChangePassword = () => {

    //Initialise the motion box for animation
    const MotionBox = motion(Box);

    //store references from fields directly
    const passwordRef = useRef();
    const confirmPasswordRef = useRef();

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
                navigate("/detective");
            }
        }
        else{
            //Error for when passwords don't match
            alert("Passwords do not match");
        }
    };

    
    return (
        //Main container
        <Flex
            minH={'100vh'} //take full viewport height
            align={'center'} //vertically center
            justify={'center'} //horizontal center
        >
            {/*Main content stack for logo, heading and form */}
            <Stack 
                spacing={8} //space between stacked children
                mx={'auto'} //Centre stack horizontally
                maxW={'lg'} //Max width
                py={12} // p-top and p-bottonm
                px={6} // p-left and p-right
            >
                {/*Header section with logo and animated title*/}
                <Stack align={'center'}>
                    {/*Logo*/}
                    <Image src="/src/Components/Assets/Logo.jpg" alt="Logo" boxSize="250px" mb={4} />

                    {/*Animated heading with typewriter effect*/}
                    <Heading color={'black'} fontSize={'4xl'}>
                        <Typewriter
                            words={['Change your Password',]} //Text that will be typed
                            loop={1} //amount of times animation plays
                            cursor //Blinking cursor
                            cursorStyle="_"
                            typeSpeed={70} //typing speed in ms
                            deleteSpeed={50} //deletion speed in ms
                            delaySpeed={1000} //Delay before starting in ms
                        />
                    </Heading>

                    {/* Subtitle */}
                    <Text fontSize={'lg'} color={'gray.600'}>
                        Don't forget it this time!
                    </Text>
                </Stack>

                {/*Main form with animation*/}
                <MotionBox
                    rounded={'lg'} //rounded corners
                    bg={"white"}   //background
                    boxShadow={'lg'} //Shadow-effect behind card
                    p={8} //padding
                    w="500px"   //fixed width

                    //Animation properties
                    initial={{ opacity: 0, scale: 0.8 }} //Starts invisible and small
                    animate={{ opacity: 1, scale: 1 }} //Animates to full size
                    transition={{ duration: 0.5, ease: 'easeOut' }} //Transition timing
                >
                    {/*Form fields container*/}
                    <Stack spacing={4}>
                    
                        {/*New Password Field */}
                        <FormControl id="password" isRequired>
                            <Stack>
                                {/* Password input with built-in show/hide toggle */}
                                <Field.Root>
                                    <Field.Label>Password</Field.Label>
                                        <PasswordInput ref={passwordRef}/>
                                </Field.Root>
                                {/* Visual indicator for password strength */}
                                <PasswordStrengthMeter value={2} />
                            </Stack>
                        </FormControl>

                        {/* Confim Password Field */}
                        <FormControl id="confirm-password" isRequired>
                            <Stack>
                                {/* Second password input input for confirmation */}
                                <Field.Root>
                                    <Field.Label>Confirm Password</Field.Label>
                                        <PasswordInput ref={confirmPasswordRef}/>
                                </Field.Root>
                            </Stack>
                        </FormControl>

                        {/* Submit button section */}
                        <Stack spacing={6} pt={6}>
                            <Button
                                bg={'black'} //Black background
                                color={'white'} //White text
                                _hover={{ //hover state styling
                                bg: 'blackAlpha.800',}}
                                onClick={handleSubmit} //Click handler
                            >
                                Submit
                            </Button>
                        </Stack>

                    </Stack>
                    
                </MotionBox>
            </Stack>



        </Flex>
    )
}

export default ChangePassword