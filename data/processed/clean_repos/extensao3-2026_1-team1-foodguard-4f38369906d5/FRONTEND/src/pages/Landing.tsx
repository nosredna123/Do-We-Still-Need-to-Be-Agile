import NavBar from "@/components/navbar/Navbar";
import { Hero } from "@/components/landing/Hero";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { Team } from "@/components/landing/Team";
import { Footer } from "@/components/landing/Footer";

const Landing = () => {
  return (
    <div className="min-h-screen bg-white">
      <NavBar variant="home" />
      <main>
        <Hero />
        <HowItWorks />
        <Team />
      </main>
      <Footer />
    </div>
  )
}

export default Landing
