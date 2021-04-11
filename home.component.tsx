import React from 'react';
import { StyleSheet } from 'react-native';

import { SafeAreaView } from 'react-native';
import { Button, Divider, Layout, TopNavigation } from '@ui-kitten/components';
import { Input } from '@ui-kitten/components';
const useInputState = (initialValue = '') => {
    const [value, setValue] = React.useState(initialValue);
    return { value, onChangeText: setValue };
  };
  
export const HomeScreen = ({ navigation }) => {
    const mediumInputState = useInputState();

  const navigateDetails = () => {
    navigation.navigate('Details');
  };

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <TopNavigation title='Cook My List' alignment='center'/>

      <Divider/>
      <Layout style={{ flex: 1, justifyContent: 'top', alignItems: 'center' }}>
      <Input
        style={styles.input}
        size='medium'
        placeholder='Search'
        {...mediumInputState}
      />

        <Button onPress={navigateDetails}>Search</Button>
      </Layout>
    </SafeAreaView>
  );
};


const styles = StyleSheet.create({
    input: {
      marginVertical: 2,
    },
  });