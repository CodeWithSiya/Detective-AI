import React, { useState } from 'react';
import { FormControl, FormLabel } from '@chakra-ui/form-control';
import { motion } from 'framer-motion'
import { Typewriter } from 'react-simple-typewriter';
import { Link as RouterLink } from "react-router-dom";

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

const ForgotPassword = () => {

    const MotionBox = motion(Box);

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
                <Image src="/src/Components/Assets/Logo.jpg" alt="Logo" boxSize="250px" mb={4} />

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
                <Heading color={'black'} lineHeight={1.1} fontSize={{ base: '2xl', md: '3xl' }}>
                    Forgot your password?
                </Heading>

                <Text
                    fontSize={{ base: 'sm', sm: 'md' }}
                    color={'gray.600'}>
                    You&apos;ll get an email with a reset link
                </Text>

                <FormControl id="email">
                    <Input
                    placeholder="your-email@example.com"
                    _placeholder={{ color: 'gray.500' }}
                    type="email"
                    />
                </FormControl>

                <Stack spacing={6}>
                    <Button
                        bg={'black'}
                        color={'white'}
                        _hover={{
                        bg: 'blackAlpha.800',
                    }}>
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


