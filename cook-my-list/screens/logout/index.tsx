
import React from "react";
import { StyleSheet } from "react-native";

import { SafeAreaView } from "react-native";
import { Divider, Layout, Button, Text } from "@ui-kitten/components";
import { LogoutScreenProps } from "../../types";

import TopNav from "../../widgets/topnav.component";

export const LogoutScreen = ({ navigation }: LogoutScreenProps): JSX.Element => {
  return (
    <SafeAreaView style={{ flex: 1 }}>
      <TopNav navigation={navigation} />

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
