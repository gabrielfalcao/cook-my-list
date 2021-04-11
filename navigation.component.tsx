import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { HomeScreen } from "./home.component";
import { DetailsScreen } from "./details.component";
import { LogoutScreen } from "./logout.component";
import { StyleSheet } from "react-native";

import { createDrawerNavigator } from "@react-navigation/drawer";
import {
  Drawer,
  DrawerItem,
  Layout,
  Avatar,
  Text,
  IndexPath,
} from "@ui-kitten/components";

const { Navigator, Screen } = createDrawerNavigator();

const DrawerHeader = ({ ...props }) => (
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
        console.log(`DrawerContent ${JSON.stringify(index)}`, state.routeNames)
        navigation.navigate(state.routeNames[index.row])}}
  >
    <DrawerItem title="Cozinhar Agora" />
    <DrawerItem title="Minhas Receitas" />
    <DrawerItem title="Logout" />
  </Drawer>
);

const HomeNavigator = () => (
  <Navigator drawerContent={(props) => <DrawerContent {...props} />}>
    <Screen name="Home" component={HomeScreen} />
    <Screen name="Receita" component={DetailsScreen} />
    <Screen name="Logout" component={LogoutScreen} />
  </Navigator>
);

export const AppNavigator = () => (
  <NavigationContainer>
    <HomeNavigator />
  </NavigationContainer>
);

const styles = StyleSheet.create({
  drawer: {
    paddingTop: 40,
  },
  topContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  card: {
    flex: 1,
    margin: 2,
  },
  container: {
    flex: 1,
    marginTop: 50,
    justifyContent: "flex-start",
    alignItems: "center",
    maxHeight: 80
  },
  avatar: {
    margin: 8,
  },
  footerContainer: {
    flexDirection: "row",
    justifyContent: "flex-end",
  },
  footerControl: {
    marginHorizontal: 2,
  },
});
