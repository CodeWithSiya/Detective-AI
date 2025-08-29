/**
 * VerifyEmail Component
 * 
 * Provides an interface for users to verify their email address using a PIN code
 * 
 * authors: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 22/08/2025
 */

import React from 'react';
import { motion } from 'framer-motion'
import { Typewriter } from 'react-simple-typewriter';
import { useNavigate } from "react-router-dom";
import { PinInput } from "@chakra-ui/react"

// Import utility function to get the email from the forgot password step
import { getEmail } from './ForgotPassword';

// Chakra UI components for styling and layout
import {
  Box,
  Flex,
  Heading,
  Image,
  Button,
  Text,
  Stack,
} from "@chakra-ui/react";

/**
 * Renders the component for email verfication
 * @returns {JSX.Element} The VerifyEmail component
 */
const VerifyEmail = () => {

    //Initialise motion box for animation
    const MotionBox = motion(Box);

    //Initialise navigator for navigation between routes
    const navigate = useNavigate();

    /**
     * Handles form submission when the "Verify" button is clicked
     * @param {Event} e 
     */
    const handleSubmit = (e) => {
        // Prevents default submit behaviour
        e.preventDefault();

        //goes to change password page
        navigate('/change-password');
    }

    return (
         // Main container
        <Flex
            minH={'100vh'} //take full height
            align={'center'} //vertically center
            justify={'center'} //horizontal center
        >
            {/* Main content stack */}
            <Stack 
                align={'center'}
                spacing={4} //space between stacked children
                mx={'auto'} //Centre stack horizontally
                maxW={'lg'} //Max width
                py={10} // p-top and p-bottonm
                px={6} // p-left and p-right
            >
                 {/* Header section */}
                <Stack align={'center'}>

                    {/*Logo*/}
                    <Image src="/src/Components/Assets/Logo.jpg" alt="Logo" boxSize="250px" mb={4} />

                    {/* Animated header */}
                    <Heading fontSize={'4xl'} color={'black'}>
                        <Typewriter
                            words={['Verify your Email']}
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
                        We have sent a code to your email!
                    </Text>
                </Stack>

                {/* Verify form with animation */}
                <MotionBox
                w='500px'
                p={6}
                my={12}
                rounded={'lg'}
                bg={"white"}
                boxShadow={'lg'}

                //Animate box
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                >
                {/* Form container */}
                <Stack
                spacing={12}
                >
                
                {/* email address */}
                <Text
                    fontSize={{ base: 'sm', sm: 'md' }}
                    color={'black'}
                    fontWeight={'bold'}
                    pb={6}
                >
                    {getEmail()}
                </Text>

                
                {/* Pin input component */}
                <PinInput.Root otp>
                    <PinInput.HiddenInput />
                    <PinInput.Control>
                        <PinInput.Input index={0} />
                        <PinInput.Input index={1} />
                        <PinInput.Input index={2} />
                        <PinInput.Input index={3} />
                    </PinInput.Control>
                </PinInput.Root>


                {/* Submit button section */}
                <Stack spacing={6} pt={6}>
                    <Button
                        bg={'black'}
                        color={'white'}
                        _hover={{
                        bg: 'blackAlpha.800',}}
                        onClick={handleSubmit}
                    >
                        Verify Email
                    </Button>
                </Stack>

            </Stack>
            </MotionBox>

            </Stack>

        

            


        </Flex>
    )

};

export default VerifyEmail