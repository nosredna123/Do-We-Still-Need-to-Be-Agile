import { View, Text, TouchableOpacity, StyleSheet, StatusBar, Image } from "react-native"
import { router } from "expo-router"

export default function HomeScreen() {
  const handleVisitorChat = () => {
    router.push("/home/chat")
  }

  const handleStudentChat = () => {
    router.push("/home/login")
  }

  return (
    <View style={styles.container}>
      <StatusBar backgroundColor="#4CAF50" barStyle="light-content" />

      <View style={styles.topBar} />

      <View style={styles.content}>
        <Text style={styles.welcomeText}>Bem vindo ao</Text>
        <Text style={styles.botName}>Uecencontra</Text>

        <View style={styles.iconContainer}>
          <Image source={require("../../public/UECE_2023.png")} style={styles.ueceLogoImage} resizeMode="contain" />
        </View>
      </View>

      <View style={styles.buttonContainer}>
        <TouchableOpacity style={styles.startButton} onPress={handleVisitorChat}>
          <Text style={styles.buttonText}>Iniciar chat como visitante</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.startButton} onPress={handleStudentChat}>
          <Text style={styles.buttonText}>Iniciar chat como aluno</Text>
        </TouchableOpacity>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  topBar: {
    height: 60,
    backgroundColor: "#4CAF50",
    width: "100%",
  },
  content: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 20,
  },
  welcomeText: {
    fontSize: 24,
    color: "#666",
    textAlign: "center",
    marginBottom: 5,
  },
  botName: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#333",
    textAlign: "center",
    marginBottom: 40,
  },
  iconContainer: {
    alignItems: "center",
    marginBottom: 60,
  },
  ueceLogoImage: {
    width: 120,
    height: 120,
  },
  buttonContainer: {
    paddingHorizontal: 20,
    paddingBottom: 50,
    gap: 15,
  },
  startButton: {
    backgroundColor: "#4CAF50",
    paddingVertical: 15,
    paddingHorizontal: 40,
    borderRadius: 25,
    alignItems: "center",
  },
  buttonText: {
    color: "white",
    fontSize: 18,
    fontWeight: "600",
  },
})
