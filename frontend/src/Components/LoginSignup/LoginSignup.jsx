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
} from "@chakra-ui/react";

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
            <VStack 
                spacing={8} //space between stacked children
                mx={'auto'} //Centre stack horizontally
                maxW={'lg'} //Max width
                py={12} // p-top and p-bottonm
                px={6} // p-left and p-right
            ></VStack>

            <VStack align={'center'}>
                <Heading fontSize={'4x1'}>Welcome back ☺️</Heading>
                <Text fontSize={'lg'} color={'gray.600'}>
                    Log in to your account to continue
                </Text>
            </VStack>

            {/*Card */}
            <Box
                rounded={'lg'} //rounded corners
                bg={"white"}
                boxShadow={'lg'} //Shadow-effect behind card
                p={8} //padding
            >
                <VStack spacing={4}>

                    <FormControl id="email">
                        <FormLabel>Email address</FormLabel>
                        <Input type="email" />
                    </FormControl>

                </VStack>
                
            </Box>




        </Flex>
    );
};
