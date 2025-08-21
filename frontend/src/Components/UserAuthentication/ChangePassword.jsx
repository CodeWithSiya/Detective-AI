import React, { useRef } from 'react';
import { FormControl, FormLabel } from '@chakra-ui/form-control';
import { motion } from 'framer-motion'
import { Typewriter } from 'react-simple-typewriter';
import { Link as RouterLink } from "react-router-dom";
import { useNavigate } from 'react-router-dom';

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
import { getEmail } from './ForgotPassword';
import { changePassword } from './AuthHandler';


const ChangePassword = () => {

    const MotionBox = motion(Box);

    //store references 
    
    const passwordRef = useRef();
    const confirmPasswordRef = useRef();

    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        
        const password = passwordRef.current.value;
        const confirmPassword = confirmPasswordRef.current.value;

        if (password === confirmPassword){

            //Mock backend behaviour
            const result = changePassword(getEmail(), password);

            alert(result.message);

            //move to main page when password is changee
            if (result.success){
                navigate("/detective");
            }
        }
        else{
            alert("Passwords do not match");
        }
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
                            words={['Change your Password',]}
                            loop={1}
                            cursor
                            cursorStyle="_"
                            typeSpeed={70}
                            deleteSpeed={50}
                            delaySpeed={1000}
                        />
                    </Heading>
                    <Text fontSize={'lg'} color={'gray.600'}>
                        Don't forget it this time!
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
                    
                        <FormControl id="password" isRequired>
                            <Stack>
                                <Field.Root>
                                    <Field.Label>Password</Field.Label>
                                        <PasswordInput ref={passwordRef}/>
                                </Field.Root>
                                <PasswordStrengthMeter value={2} />
                            </Stack>
                        </FormControl>

                        <FormControl id="confirm-password" isRequired>
                            <Stack>
                                <Field.Root>
                                    <Field.Label>Confirm Password</Field.Label>
                                        <PasswordInput ref={confirmPasswordRef}/>
                                </Field.Root>
                            </Stack>
                        </FormControl>

                        <Stack spacing={6} pt={6}>
                            <Button
                                bg={'black'}
                                color={'white'}
                                _hover={{
                                bg: 'blackAlpha.800',}}
                                onClick={handleSubmit}
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