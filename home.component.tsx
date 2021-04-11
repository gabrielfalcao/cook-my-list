import React from "react";
import { StyleSheet } from "react-native";

import { SafeAreaView } from "react-native";
import { Button, List, Divider, Layout, Text } from "@ui-kitten/components";
import { Avatar, ListItem, Icon } from "@ui-kitten/components";

import { Input } from "@ui-kitten/components";
import TopNav from "./topnav.component";
import IngredientSearch from "./ingredient-input.component";
import foodImages from "./food-images";
import {ingredients} from "./ingredients.constants"
const CloseIcon = ({...props}) => <Icon {...props} name="close-circle-outline" />;

const useIngredientData = () => {
const [data, setData] = React.useState(ingredients)
return {data, setData}
}
const useInputState = (initialValue = "") => {
  const [value, setValue] = React.useState(initialValue);
  return { value, onChangeText: setValue };
};




export const HomeScreen = ({ navigation }) => {
  const mediumInputState = useInputState();
const ingredients = useIngredientData()
  const navigateDetails = () => {
    navigation.navigate("Details");
  };

  const renderFoodItem = ({item}) => {
    const {imageName, ...info} = item
  const ImageItem = ({ ...props }) => (
    <Avatar
      {...props}
      style={[props.style, { tintColor: null }]}
      source={foodImages[imageName]}
    />
  );

  const RemoveItem = ({...props}) => (
      <Button appearance="ghost" status="danger" onPress={()=> ingredients.setData(ingredients.data.filter((zutaten) => zutaten !== item))} {...props} accessoryRight={CloseIcon}/>
  )
  return (
    <ListItem
      title={info.name}
      //description={info.description}
      accessoryLeft={ImageItem}
      accessoryRight={RemoveItem}
    />
  );
};

    const addIngredient = (zutaten) => {
        if (ingredients.data.filter((i) => i.name === zutaten.name).length === 0) {
            ingredients.setData([...ingredients.data, zutaten])
        }
    }
  return (
    <SafeAreaView style={{ flex: 1 }}>
      <TopNav />

      <Divider />
      <Layout style={{ flex: 1, justifyContent: "top", alignItems: "left",   }}>
        <Text category="s1" status="basic" style={styles.questionTitle}>
          O que temos para hoje?
        </Text>
        <IngredientSearch
          addIngredient={addIngredient}
          chosenIngredientNames={ingredients.data.map(i => i.name)}
          style={styles.input}
          size="medium"
          placeholder="Adicionar ingrediente"
          {...mediumInputState}
        />
        <List
          style={styles.container}
          contentContainerStyle={styles.contentContainer}
          data={ingredients.data}
          renderItem={renderFoodItem}
        />
      </Layout>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  input: {
    marginHorizontal: 20,
  },
  questionTitle: {
    paddingTop: 15,
    paddingBottom: 15,
    fontSize: 16,
    textAlign: "center",
    width: "100%",
    
  },
  container: {
    maxHeight: "100%",
    marginHorizontal: 20,
    marginTop: 5
  },
  contentContainer: {
      minWidth: "100%"
    
  },

});
