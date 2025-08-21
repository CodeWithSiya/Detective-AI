/**
 * Forgot Password Component
 * 
 * Provides an interface for users to initiate password reset by entering their email
 * 
 * author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 22/08/2025
 */


import React, { useRef } from 'react';
import { FormControl } from '@chakra-ui/form-control';
import { motion } from 'framer-motion'
import { Typewriter } from 'react-simple-typewriter';
import { useNavigate } from 'react-router-dom';

//Chakra UI components for styling and layout
import {
  Box,
  Flex,
  Heading,
  Image,
  Input,
  Button,
  Text,
  Stack,
  Field,
} from "@chakra-ui/react";

// Import authentication handler for email verification
import { emailExists } from './AuthHandler';



let emailValue = null;

/**
 * Function that sets the email for the password reset
 * @param {string} email 
 */
export const setEmail = (email) => {
  emailValue = email;
};

/**
 * Function that gets the email value for the password reset
 * @returns {string|null}
 */
export const getEmail = () => {
  return emailValue;
};

/**
 * Function that renders the form for forgot password component
 * @returns {JSX.Element} ForgotPasswordComponent
 */
const ForgotPassword = () => {

    //Initialise motion box for animation
    const MotionBox = motion(Box);

    //Initialise navigator for navigating between routes
    const navigate = useNavigate();

    const emailRef = useRef();

    const handleSubmit = (e) => {
        e.preventDefault();

        const result = emailExists(emailRef.current.value);

        if (result.success){
            setEmail(emailRef.current.value);

            navigate('/verify-email');
        }
        else{
            alert(result.message);
        }
        


    }

    return (
        <Flex
            minH={'100vh'} //take full height
            align={'center'} //vertically center
            justify={'center'} //horizontal center
        >
            <Stack 
                align={'center'}
                spacing={4} //space between stacked children
                mx={'auto'} //Centre stack horizontally
                maxW={'lg'} //Max width
                py={10} // p-top and p-bottonm
                px={6} // p-left and p-right
            >
                <Stack align={'center'}>
                    <Image src="/src/Components/Assets/Logo.jpg" alt="Logo" boxSize="250px" mb={4} />
                    <Heading fontSize={'4xl'} color={"black"}>
                        <Typewriter
                            words={['Forgot your Password?',]}
                            loop={1}
                            cursor
                            cursorStyle="_"
                            typeSpeed={70}
                            deleteSpeed={50}
                            delaySpeed={1000}
                        />
                    </Heading>
                    <Text fontSize={'lg'} color={'gray.600'}>
                        You&apos;ll get an email with a reset link
                    </Text>
                </Stack>
               

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
                <Stack
                spacing={4}
            >

                <FormControl id="email">
                    <Field.Root>
                        <Field.Label>Email</Field.Label>
                        <Input placeholder="johndoe@example.com" ref={emailRef}/>
                    </Field.Root>
                </FormControl>

                <Stack spacing={6} pt={6}>
                    <Button
                        bg={'black'}
                        color={'white'}
                        _hover={{
                        bg: 'blackAlpha.800',}}
                        onClick={handleSubmit}
                    >
                        Request Reset
                    </Button>
                </Stack>

            </Stack>
            </MotionBox>

            </Stack>

        

            


        </Flex>
    )

}
export default ForgotPassword;


