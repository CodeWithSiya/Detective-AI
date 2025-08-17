import React, { useState } from 'react';
import './LoginSignup.css';
import { FormControl, FormLabel } from '@chakra-ui/form-control';

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
} from "@chakra-ui/react";
import { LuTypeOutline } from 'react-icons/lu';

export const LoginSignup = () => {

    //Update state as user inputs
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [rememberMe, setRememberMe] = useState('');



    const handleSubmit = (e) => {
        //Prevent default submit behaviour
        e.preventDefault();

        //Log values to console
        console.log("Email:", email);
        console.log("Password:", password);
    };


    const handleGoogleLogin = () => {

    }

    const handleGithubLogin = () => {

    }

    const handleFacebookLogin = () => {
        
    }

    return (
        
        //Container for background
        <Flex
            minH={'100vh'} //take full height
            align={'center'} //vertically center
            justify={'center'} //horizontal center
            bgGradient={"linear(to-r, purple.600, purple.400)"} //Purple Gradient
        >
            <Stack 
                spacing={8} //space between stacked children
                mx={'auto'} //Centre stack horizontally
                maxW={'lg'} //Max width
                py={12} // p-top and p-bottonm
                px={6} // p-left and p-right
            >

                <Stack align={'center'}>
                    <Heading fontSize={'4xl'}>Welcome back ☺️</Heading>
                    <Text fontSize={'lg'} color={'gray.600'}>
                        Log in to your account to continue
                    </Text>
                </Stack>

                {/*Card */}
                <Box
                    rounded={'lg'} //rounded corners
                    bg={"white"}
                    boxShadow={'lg'} //Shadow-effect behind card
                    p={8} //padding
                    w="500px"
                >
                    <Stack spacing={4}>
                    
                        <FormControl id="email">
                            <FormLabel>Email address</FormLabel>
                            <Input type="email" />
                        </FormControl>

                        <FormControl id="password">
                            <FormLabel>Password</FormLabel>
                            <Input type="password" />
                        </FormControl>

                        <Stack
                            direction={{ base: 'column', sm: 'row' }}
                            align={'start'}
                            justify={'space-between'}
                        >
                            {/*Checkbox*/}
                            <Checkbox.Root
                                variant={'subtle'}
                                colorPalette={'purple'}
                            >
                                <Checkbox.HiddenInput />
                                <Checkbox.Control />
                                <Checkbox.Label>Remember me</Checkbox.Label>
                            </Checkbox.Root>
                            
                            <Link color="purple.500" fontSize="sm">
                                Forgot password?
                            </Link>

                        </Stack>

                        <Button
                            bg={'purple.400'}
                            variant={'subtle'}
                            color={'white'}
                            _hover={{
                            bg: 'purple.500',
                            }}
                        >
                            Log in
                        </Button>

                        <Text textAlign="center">
                                Don’t have an account?{" "}
                            <Link color="purple.600" >
                                Sign up
                            </Link>
                        </Text>

                    </Stack>
                    
                </Box>
            </Stack>



        </Flex>
    );
};
