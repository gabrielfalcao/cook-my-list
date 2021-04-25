import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { HomeScreen } from "../home";
import { RecipeDetailsScreen } from "../recipe-details";
import { MyRecipesScreen } from "../my-recipes";
import { LogoutScreen } from "../logout";
import { RootStackParamList } from "../../types";
import styles from "./styles";

import { createDrawerNavigator } from "@react-navigation/drawer";
import {
  Drawer,
  DrawerItem,
  Layout,
  Avatar,
  Text,
  IndexPath,
} from "@ui-kitten/components";

const { Navigator, Screen } = createDrawerNavigator<RootStackParamList>();

const DrawerHeader = () => (
  <Layout style={styles.container} level="1">
    <Avatar
      style={styles.avatar}
      shape="round"
      source={{
        uri:
          "https://lh3.googleusercontent.com/a-/AOh14GiNT5q-TwfcvJn4qTBGKNAWzrYb-r708sdGyHfxBxo=s78-p-k-rw-no",
      }}
    />
    <Text category="h6">Cristiane Konrath Ramires</Text>
  </Layout>
);
const DrawerContent = ({ navigation, state }) => (
  <Drawer
    selectedIndex={new IndexPath(state.index)}
    style={styles.drawer}
    header={DrawerHeader}
    onSelect={(index) => {
      //console.log(`DrawerContent ${JSON.stringify(index)}`, state.routeNames);
      navigation.navigate(state.routeNames[index.row]);
    }}
  >
    <DrawerItem title="Cozinhar Agora" />
    <DrawerItem title="Minhas Receitas" />
    <DrawerItem title="Logout" />
  </Drawer>
);

const HomeNavigator = () => (
  <Navigator drawerContent={(props) => <DrawerContent {...props} />}>
    <Screen name="Home" component={HomeScreen} />
    <Screen name="MyRecipes" component={MyRecipesScreen} />
    <Screen name="RecipeDetails" component={RecipeDetailsScreen} />
    <Screen name="Logout" component={LogoutScreen} />
  </Navigator>
);

export const AppNavigator = () => (
  <NavigationContainer>
    <HomeNavigator />
  </NavigationContainer>
);

