const mockMaps = [
  require("../public/images/mock-map-1.jpg"), // NC2A
  require("../public/images/mock-map-2.jpg"), // Reitoria
  require("../public/images/mock-map-3.jpg"), // Restaurante Universitário
  require("../public/images/mock-map-4.jpg"), // Complexo Esportivo
]

export const getRandomMockMap = () => {
  const randomIndex = Math.floor(Math.random() * mockMaps.length)
  return mockMaps[randomIndex]
}

export default mockMaps