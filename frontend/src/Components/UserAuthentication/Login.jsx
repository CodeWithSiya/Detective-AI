import React, { useRef } from 'react';
import { FormControl, FormLabel } from '@chakra-ui/form-control';
import { motion } from 'framer-motion'
import { Typewriter } from 'react-simple-typewriter';
import { Link as RouterLink } from "react-router-dom";

import {
  PasswordInput,
  PasswordStrengthMeter,
} from "@/components/ui/password-input"

import {
  Box,
  Flex,
  Heading,
  Image,
  Input,
  Button,
  Text,
  Link,
  VStack,
  Checkbox,
  Stack,
  Field,
} from "@chakra-ui/react";



export const Login = () => {
    const MotionBox = motion(Box);

    const emailRef = useRef();
    const passwordRef = useRef();

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log("Email:", emailRef.current.value);
        console.log("Password:", passwordRef.current.value);
    };

    return (
        
        //Container for background
        <Flex
            minH={'100vh'} //take full height
            align={'center'} //vertically center
            justify={'center'} //horizontal center
        >
            <Stack 
                spacing={8} //space between stacked children
                mx={'auto'} //Centre stack horizontally
                maxW={'lg'} //Max width
                py={12} // p-top and p-bottonm
                px={6} // p-left and p-right
            >

                <Stack align={'center'}>
                    <Image src="/src/Components/Assets/Logo.jpg" alt="Logo" boxSize="250px" mb={4} />

                    <Heading color={'black'} fontSize={'4xl'}>
                        <Typewriter
                            words={['Welcome back', 'Let’s get started!', 'Case files await, Detective.', 'Mystery ahead. Stay sharp.',]}
                            loop={true}
                            cursor
                            cursorStyle="_"
                            typeSpeed={70}
                            deleteSpeed={50}
                            delaySpeed={1000}
                        />
                    </Heading>
                    <Text fontSize={'lg'} color={'gray.600'}>
                        Log in to your account to continue
                    </Text>
                </Stack>

                {/*Card */}
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
                    
                        <FormControl id="email">
                            <Field.Root>
                                <Field.Label>Email</Field.Label>
                                <Input placeholder="me@example.com" />
                            </Field.Root>
                        </FormControl>

                        <FormControl id="password">
                            <Field.Root>
                                <Field.Label>Password</Field.Label>
                                <PasswordInput />
                            </Field.Root>
                        </FormControl>


                        <Stack
                            direction={{ base: 'column', sm: 'row' }}
                            align={'start'}
                            justify={'space-between'}
                        >
                            {/*Checkbox*/}
                            <Checkbox.Root
                                variant={'subtle'}
                                colorPalette={'black'}
                            >
                                <Checkbox.HiddenInput />
                                <Checkbox.Control />
                                <Checkbox.Label>Remember me</Checkbox.Label>
                            </Checkbox.Root>
                            
                            <Link 
                            as={RouterLink}
                            to="/forgot-password"
                            color="black" 
                            fontSize="sm"
                            _hover={{ color: "gray.500" }}>
                                Forgot password?
                            </Link>

                        </Stack>

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
