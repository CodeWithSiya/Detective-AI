import React, { useRef } from 'react';
import { FormControl, FormLabel } from '@chakra-ui/form-control';
import { motion } from 'framer-motion'
import { Typewriter } from 'react-simple-typewriter';
import { Link as RouterLink } from "react-router-dom";
import { PinInput } from "@chakra-ui/react"


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
  HStack
} from "@chakra-ui/react";

const handleSubmit = (e) => {

}


const VerifyEmail = () => {

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
                <Stack align={'center'}>
                    <Image src="/src/Components/Assets/Logo.jpg" alt="Logo" boxSize="250px" mb={4} />
                    <Heading fontSize={'4xl'} color={'black'}>
                        Verify your Email
                    </Heading>
                    <Text fontSize={'lg'} color={'gray.600'}>
                        We have sent a code to your email!
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
                spacing={12}
                >

                <Text
                    fontSize={{ base: 'sm', sm: 'md' }}
                    color={'black'}
                    fontWeight={'bold'}
                    pb={6}
                >
                    johndoe@gmail.com
                </Text>

                

                <PinInput.Root otp>
                    <PinInput.HiddenInput />
                    <PinInput.Control>
                        <PinInput.Input index={0} />
                        <PinInput.Input index={1} />
                        <PinInput.Input index={2} />
                        <PinInput.Input index={3} />
                    </PinInput.Control>
                </PinInput.Root>

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