/**
 * Forgot Password Component
 * 
 * Provides an interface for users to initiate password reset by entering their email
 * 
 * author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
 * version: 10/09/2025
 */


import React, { useRef } from 'react';
import "./ForgotPassword.css";
import { Typewriter } from 'react-simple-typewriter';
import { useNavigate } from 'react-router-dom';
// Import authentication handler for email verification
import { emailExists } from '../AuthHandler';

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

    //Create ref to access email input field
    const emailRef = useRef();

    /**
     * Function gets called when the submit button gets pressed
     * @param {Event} e 
     */
    const handleSubmit = (e) => {
        //prevents default submission behaviour
        e.preventDefault();

        // Check if the entered email exists in the sytem
        const result = emailExists(emailRef.current.value);

        if (result.success){
            //If found
            setEmail(emailRef.current.value);

            navigate('/verify-email');
        }
        else{
            //Error message if not found/invalid
            alert(result.message);
        }
        


    }

    return (

        //Main container
        <Flex
            minH={'100vh'} //take full viewport height
            align={'center'} //vertically center
            justify={'center'} //horizontal center
        >
            {/* Main content stack*/}
            <Stack 
                align={'center'} //Center children horizontally
                spacing={4} //space between stacked children
                mx={'auto'} //Centre stack horizontally
                maxW={'lg'} //Max width
                py={10} // p-top and p-bottonm
                px={6} // p-left and p-right
            >
                {/* Log and header section */}
                <Stack align={'center'}>

                    {/*Logo*/}
                    <Image src="/src/Components/Assets/Logo.jpg" alt="Logo" boxSize="250px" mb={4} />

                    {/* Heading with typewriter effect */}
                    <Heading fontSize={'4xl'} color={"black"}>
                        <Typewriter
                            words={['Forgot your Password?',]} //what will be typed
                            loop={1}//amount of times animation plays
                            cursor //Blinking cursor
                            cursorStyle="_"
                            typeSpeed={70} //typing speed in ms
                            deleteSpeed={50} //deletion speed in ms
                            delaySpeed={1000} //Delay before starting in ms
                        />
                    </Heading>

                    {/*Subtitle*/}
                    <Text fontSize={'lg'} color={'gray.600'}>
                        You&apos;ll get an email with a reset link
                    </Text>
                </Stack>
               
                {/* Main form with animation */}
                <MotionBox
                w='500px' //fixed width
                p={6}      //internal padding
                my={12} //Vertical margin
                rounded={'lg'} //large rounded corners
                bg={"white"}  //White background
                boxShadow={'lg'} //large shadow drop

                //Animate box
                initial={{ opacity: 0, scale: 0.8 }} //Start small and invisible
                animate={{ opacity: 1, scale: 1 }} //Animate to visible and full size
                transition={{ duration: 0.5, ease: 'easeOut' }} //Smooth transition
            >
                {/* Form container */}
                <Stack spacing={4}>

                {/* Email input field */}
                <FormControl id="email">
                    <Field.Root>
                        <Field.Label>Email</Field.Label>
                        <Input placeholder="johndoe@example.com" ref={emailRef}/>
                    </Field.Root>
                </FormControl>

                {/* Submit button section */}
                <Stack spacing={6} pt={6}>

                    <Button
                        bg={'black'} //black background
                        color={'white'}  //white text
                        _hover={{   //Hover state styling
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


