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
import Logo from '../../Assets/Logo.jpg';
import { Typewriter } from 'react-simple-typewriter';
import { Link as RouterLink, useNavigate } from "react-router-dom";
import {Eye, EyeOff} from 'lucide-react';
import { login } from '../AuthHandler';

/**
 * Function that renders the main login page
 * @returns {JSX.Element} Login Component
 */
export const Login = () => {
    //Inititialise motion box
    const MotionBox = motion(Box);

    //store references for email and password
    const emailRef = useRef();
    const passwordRef = useRef();

    //Initialise navigation between routes
    const navigate = useNavigate();

    /**
     * Gets called when submit button is clicked
     * @param {Event} e 
     */
    const handleSubmit = (e) => {

        //prevent default behaviour
        e.preventDefault();

        //Extract current values from input fields
        const email = emailRef.current.value;
        const password = passwordRef.current.value;

        //Mock backend behaviour by attempting to autheticate user
        const result = login(email, password);

        //move to next page if login successful
        if (result.success){
            navigate("/detective");
        }
        else{
            //Error message
            alert(result.message);
        }
    };

    return (
        
        //Main container
        <Flex
            minH={'100vh'} //take full viewport height
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

                    {/*Logo*/}
                    <Image src="/src/Components/Assets/Logo.jpg" alt="Logo" boxSize="250px" mb={4} />

                    {/* Heading with typewriter animation */}
                    <Heading color={'black'} fontSize={'4xl'}>
                        <Typewriter
                            words={['Welcome back!', 'Let’s get started!', 'Case files await, Detective.', 'Mystery ahead. Stay sharp.','What are you waiting for?','Time to catch AI!'
                            ]} //Message that rotate
                            loop={true} //Continuosly loops
                            cursor //Blinking cursor
                            cursorStyle="_" //underscore
                            typeSpeed={70}  //Speed of typing in ms
                            deleteSpeed={50} //Delete speed in ms
                            delaySpeed={1000} //Pause between messages in ms
                        />

                    {/* Subtitle */}
                    </Heading>
                    <Text fontSize={'lg'} color={'gray.600'}>
                        Log in to your account to continue
                    </Text>
                </Stack>

                {/* Login form with animation */}
                <MotionBox
                    rounded={'lg'} //rounded corners
                    bg={"white"} //white background
                    boxShadow={'lg'} //Shadow-effect behind card
                    p={8} //padding
                    w="500px" //fixed width

                    //Animate box
                    initial={{ opacity: 0, scale: 0.8 }} //Start small and invisible
                    animate={{ opacity: 1, scale: 1 }} //Animate to full size and visibility
                    transition={{ duration: 0.5, ease: 'easeOut' }} //Smooth transition
                >
                    {/* Field container */}
                    <Stack spacing={4}>
                    
                        {/* Email input field */}
                        <FormControl id="email">
                            <Field.Root>
                                <Field.Label>Email</Field.Label>
                                <Input placeholder="me@example.com" ref={emailRef}  w="100%"/>
                            </Field.Root>
                        </FormControl>

                         {/* Password input field with show/hide toggle */}
                        <FormControl id="password">
                            <Field.Root>
                                <Field.Label>Password</Field.Label>
                                <PasswordInput ref={passwordRef}  w="100%"/>
                            </Field.Root>
                        </FormControl>

                        {/* Remember me checkbox and forgot password link */}
                        <Stack
                            direction={{ base: 'column', sm: 'row' }}
                            align={'start'}
                            justify={'space-between'}
                        >
                            {/*Checkbox*/}
                            <Checkbox.Root
                                variant={'subtle'} //style
                                colorPalette={'black'} //black colour
                            >
                                <Checkbox.HiddenInput />
                                <Checkbox.Control />
                                <Checkbox.Label>Remember me</Checkbox.Label>
                            </Checkbox.Root>
                            
                            {/* Forgot password link */}
                            <Link 
                            as={RouterLink} //React Router link component
                            to="/forgot-password" //go to Forgot Password
                            color="black" 
                            fontSize="sm"
                            _hover={{ color: "gray.500" }}>
                                Forgot password?
                            </Link>

                        </Stack>

                        {/* login submit button */}
                        <Button
                            bg={'black'}
                            variant={'solid'}
                            color={'white'}
                            _hover={{
                            bg: 'blackAlpha.800',
                            }}
                            onClick={handleSubmit}
                        >
                            Log in
                        </Button>


                        {/* Sign up link for users without accounts */}
                        <Text textAlign="center">
                                Don’t have an account?{" "}
                            <Link 
                                as={RouterLink} 
                                to="/signup" 
                                color="black" 
                                _hover={{ color: "gray.500" }}>
                                Sign up
                            </Link>
                        </Text>

                    </Stack>
                    
                </MotionBox>
            </Stack>



        </Flex>
    );
};

export default Login
