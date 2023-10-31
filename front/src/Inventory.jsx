import {
  Flex,
  Box,
  FormControl,
  FormLabel,
  Input,
  HStack,
  useToast,
  Stack,
  Button,
  Heading,
  useColorModeValue,
  Select,
  Textarea,
  FormErrorMessage,
} from '@chakra-ui/react';

import React from 'react';
import { useForm } from 'react-hook-form';
import { Layout } from './layout/Layout';
import { command } from './commander';
// import { useMutation } from '@apollo/client';

// import { CREATE_TEAM } from '../api/teams';

export default function Inventory() {
  //const [createTeam, { loading }] =
  //  useMutation(CREATE_TEAM);


  const [headerText, setHeaderText] = React.useState("")
  const [contentText, setContentText] = React.useState("")
  const toast = useToast();

  const {
    handleSubmit,
    register,
    formState: { errors },
  } = useForm();

  const onSubmit = async data => {
    const[header, content] = await command(data.text,data.user,"6540555864259e2dc2ba899b");
    setHeaderText(header)
    
    setContentText(content)

    toast({
      title: 'Submitted',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };

  return (
    <Layout>
      <Flex align={'center'} justify={'center'}>
        <Stack spacing={8} mx={'auto'} py={12} px={6}>
          <Stack align={'center'}>
            <Heading fontSize={'4xl'} textAlign={'center'}>
              Enter a command to build your dream farm!!🌱
            </Heading>
            <Heading fontSize={'1xl'} textAlign={'center'}>
              If you need help enter "info" in the chat
            </Heading>
          </Stack>
          <form onSubmit={handleSubmit(onSubmit)}>
            <Box
              rounded={'lg'}
              bg={useColorModeValue('white', 'gray.700')}
              boxShadow={'lg'}
              p={8}
            >
              <Stack spacing={4}>
                <HStack>
                  <Box>
                    <FormControl id="user" isRequired>
                      <FormLabel>User type</FormLabel>
                      <Select
                        placeholder="Selecciona opción"
                        {...register('user')}
                      >
                        <option value="Player">Player</option>
                        <option value="Admin">Admin</option>
                      </Select>
                      <FormErrorMessage>
                        {errors.user && errors.user.message}
                      </FormErrorMessage>
                    </FormControl>
                  </Box>
                </HStack>
                <FormControl id="text" isRequired>
                  <FormLabel>Enter command here</FormLabel>
                  <Textarea {...register('text')} />
                  <FormErrorMessage>
                    {errors.text && errors.text.message}
                  </FormErrorMessage>
                </FormControl>
                <Stack spacing={10} pt={2}>
                  <Button
                    loadingText="Loading..."
                    size="lg"
                    bg={'blue.400'}
                    color={'white'}
                    type="submit"
                    isLoading={false}
                    _hover={{
                      bg: 'blue.500',
                    }}
                  >
                    Send
                  </Button>
                </Stack>
              </Stack>
            </Box>
          </form>
          <Box
              rounded={'lg'}
              bg={useColorModeValue('white', 'gray.700')}
              boxShadow={'lg'}
              p={8}
            >
              <Stack spacing={4}>
                <Heading fontSize={'4xl'} textAlign={'center'}>
                  {headerText}
                </Heading>
                <Heading fontSize={'2xl'} textAlign={'center'}>
                  {contentText}
                </Heading>
              </Stack>
            </Box>
        </Stack>
      </Flex>
    </Layout>
  );
}
