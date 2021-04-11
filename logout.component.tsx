import React from "react";
import { StyleSheet } from "react-native";

import { SafeAreaView } from "react-native";
import {
  Divider,
  Icon,
  Layout,
  ButtonGroup,
  Button,
  Text,
  TopNavigation,
  TopNavigationAction,
} from "@ui-kitten/components";

const BackIcon = (props) => <Icon {...props} name="arrow-back" />;

export const LogoutScreen = ({ navigation }) => {
  const navigateBack = () => {
    navigation.goBack();
  };

  const BackAction = () => (
    <TopNavigationAction icon={BackIcon} onPress={navigateBack} />
  );

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <TopNavigation
        title="MyApp"
        alignment="center"
        accessoryLeft={BackAction}
      />
      <Divider />
      <Layout style={styles.layout}>
        <Text style={styles.title} category="h4">
          Tem certeza que deseja sair ?
        </Text>

        <Button
          onPress={() => {
            navigation.navigate("Home");
          }}
          status="success"
          size="giant"
          style={styles.button}
        >
          Sim
        </Button>
        <Button
          onPress={() => {
            navigation.navigate("Home");
          }}
          status="danger"
          size="giant"
          style={styles.button}
        >
          Não
        </Button>
      </Layout>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  button: {
    margin: 10,
  },
  title: { marginTop: 100 },
  layout: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
  },
});
