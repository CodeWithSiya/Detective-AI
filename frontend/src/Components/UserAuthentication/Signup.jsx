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
  HStack,
  Field,
} from "@chakra-ui/react";



const Signup = () => {

    const MotionBox = motion(Box);

    const nameRef = useRef();
    const emailRef = useRef();
    const passwordRef = useRef();
    const lastNameRef = useRef();

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log("First Name:", nameRef.current.value);
        console.log("Last Name:", lastNameRef.current.value);
        console.log("Email:", emailRef.current.value);
        console.log("Password:", passwordRef.current.value);
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
                    <Image src="/src/Components/Assets/Logo.jpg" alt="Logo" boxSize="250px" mb={4} />
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
                    <Text fontSize={'lg'} color={'gray.600'}>
                        Create an account to continue
                    </Text>
                </Stack>

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
                                <FormControl id="firstName">
                                    <Field.Root required>
                                        <Field.Label>Name<Field.RequiredIndicator /></Field.Label>
                                            <Input placeholder="e.g. John" />
                                    </Field.Root>
                                </FormControl>
                            </Box>
                            <Box flex={1}> 
                                <FormControl id="lastName">
                                    <Field.Root>
                                        <Field.Label>Surname</Field.Label>
                                            <Input placeholder="e.g. Doe" />
                                    </Field.Root>
                                </FormControl>
                            </Box>
                        </HStack>

                        <FormControl id="email">
                            <Field.Root required>
                                <Field.Label>Email<Field.RequiredIndicator /></Field.Label>
                                    <Input placeholder="johndoe@example.com" />
                            </Field.Root>
                        </FormControl>

                        <FormControl id="password" isRequired>
                            <Stack>
                                <Field.Root required>
                                    <Field.Label>Password<Field.RequiredIndicator /></Field.Label>
                                        <PasswordInput />
                                </Field.Root>
                                <PasswordStrengthMeter value={2} />
                            </Stack>
                        </FormControl>

                        <FormControl id="confirm-password">
                            <Stack>
                                <Field.Root required>
                                    <Field.Label>Confirm Password<Field.RequiredIndicator /></Field.Label>
                                        <PasswordInput />
                                </Field.Root>
                            </Stack>
                        </FormControl>

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