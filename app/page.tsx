"use client";

import Navbar from "./components/Landing/Navbar";
import Hero from "./components/Landing/Hero";
import CTA from "./components/Landing/CTA";
import Footer from "./components/Landing/Footer";

export default function Home() {
  return (
    <div>
      <Navbar />
      <Hero />
      <CTA />
      <Footer />
    </div>
  );
}
