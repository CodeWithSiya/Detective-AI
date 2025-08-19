import React, { useRef } from 'react';
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

const handleSubmit = (e) => {

}


const ChangePassword = () => {

    const MotionBox = motion(Box);

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
                            words={['Change your Password']}
                            loop={true}
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
                    
                        <FormControl id="password">
                            <FormLabel>Password</FormLabel>
                            <Input 
                            type="password" 
                            />
                        </FormControl>

                        <FormControl id="confirm-password">
                            <FormLabel>Confirm Password</FormLabel>
                            <Input 
                            type="password" 
                            />
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