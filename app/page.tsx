import Hero from "@/components/home/Hero";
import ProblemSection from "@/components/home/ProblemSection";
import IntroVideo from "@/components/home/IntroVideo";
import SolutionsGrid from "@/components/home/SolutionsGrid";
import ProcessSteps from "@/components/home/ProcessSteps";
import FeaturedProduct from "@/components/home/FeaturedProduct";
import AutomationShowcase from "@/components/home/AutomationShowcase";
import WhyGos from "@/components/home/WhyGos";
import FinalCTA from "@/components/common/FinalCTA";

export default function Home() {
  return (<><Hero /><ProblemSection /><IntroVideo /><SolutionsGrid /><ProcessSteps /><FeaturedProduct /><AutomationShowcase /><WhyGos /><FinalCTA /></>);
}
