low_ndvi_air = [
    "Reforestation",  # Planting trees to improve air quality and restore vegetation.
    "Urban Greening",  # Adding plants and trees to urban spaces to reduce pollution and increase greenery.
    "Agroforestry", # Planting trees alongside crops to improve soil health and reduce pollution effects.
    "Green Infrastructure",  # Creating urban green spaces such as parks, green roofs, and tree-lined streets.
    "Air Quality Monitoring",  # Setting up monitoring systems to track and respond to air quality issues.
    "Community Tree Planting",  # Local efforts to plant trees in communities, improving both air quality and NDVI.
    "Eco-friendly Public Transport Systems",  # Promoting clean transport to reduce emissions and improve air quality.
    "Pollution-Absorbing Green Walls",  # Installing green walls in cities to absorb pollutants and improve air quality.
    "Bioremediation with Plants",  # Using plants to absorb toxins and pollutants in the environment.
    "Green Energy Solutions",  # Implementing solar, wind, or other renewable energy solutions to reduce air pollution from traditional energy sources.
    "Permeable Pavements and Green Streets",  # Designing cities with permeable pavements and more green streets to help reduce air pollution and increase vegetation.
    "Wetlands Restoration",  # Rehabilitating wetlands which can act as natural air filters and restore biodiversity.
    "Pollution-Controlled Urban Parks",  # Creating parks with specific plants that reduce air pollution while adding greenery.
    "Sustainable Agriculture Practices",  # Introducing organic farming and sustainable practices that improve land and air quality.
    "Windbreaks and Shelters",  # Planting rows of trees to reduce dust and air pollution in rural or agricultural areas.
    "Environmental Education for Pollution Control",  # Educating local communities on reducing pollution and improving green spaces.
    "Recycling and Waste Reduction Programs",  # Encouraging recycling initiatives to reduce air pollution and improve sustainability.
]

high_ndvi_air = [
    "Eco-Tourism",  # Promoting sustainable tourism in areas with high vegetation and good air quality.
    "Biodiversity Conservation",  # Protecting and maintaining ecosystems to preserve biodiversity.
    "Sustainable Agriculture Practices",  # Implementing organic or permaculture techniques to enhance soil and air quality.
    "Forest Conservation",  # Protecting existing forests and maintaining their role in air purification and carbon sequestration.
    "Wildlife Habitat Restoration",  # Restoring and preserving wildlife habitats to ensure biodiversity and ecosystem health.
    "Green Energy Projects",  # Investing in renewable energy solutions (solar, wind, etc.) to maintain air quality and reduce carbon footprint.
    "Pollution-Free Urban Development",  # Developing urban areas with eco-friendly designs, including green buildings, green roofs, and sustainable transport.
    "Water Conservation and Management",  # Projects that improve water efficiency while preserving natural ecosystems.
    "Carbon Sequestration",  # Projects focused on increasing carbon capture through forest expansion or soil health improvement.
    "Rainwater Harvesting",  # Collecting and storing rainwater for agricultural and domestic use to reduce water stress.
    "Ecosystem-based Adaptation Projects",  # Utilizing natural ecosystems to adapt to climate change while ensuring sustainability.
    "Conservation Agriculture",  # Practices that increase soil health and productivity while maintaining high vegetation cover.
    "Urban Farming and Local Food Systems",  # Promoting local food production in urban areas, reducing food miles and pollution.
    "Agroecology",  # Applying ecological principles to agricultural systems, focusing on sustainable and resilient practices.
    "Sustainable Forestry",  # Implementing responsible forestry practices that protect both the forest ecosystem and air quality.
    "Green Infrastructure in Cities",  # Creating green spaces, parks, and green roofs in urban areas to enhance the quality of life and maintain air quality.
    "Rewilding Projects",  # Restoring natural processes by reintroducing species and allowing ecosystems to regenerate naturally.
    "Climate-Smart Agriculture",  # Promoting agricultural practices that are resilient to climate change while enhancing productivity and sustainability.
    "Community-Based Conservation",  # Involving local communities in the management and protection of natural resources.
]

moderate_ndvi_air = [
    "Sustainable Agriculture Practices",  # Implementing organic farming methods in areas with moderate vegetation and air quality.
    "Eco-friendly Public Transport Systems",  # Encouraging low-emission transportation options to improve urban air quality.
    "Pollution-Controlled Urban Parks",  # Developing green spaces with specific plants that help to improve air quality.
    "Water Conservation and Management",  # Implementing systems to conserve water while promoting sustainable ecosystem management.
    "Agroforestry",  # Integrating trees with crops to enhance soil health and moderate the environmental impact of agriculture.
    "Green Infrastructure",  # Building green roofs, urban forests, and sustainable water systems to manage urban heat islands.
    "Community Tree Planting",  # Involving communities in planting trees to improve air quality and promote local environmental benefits.
    "Waste-to-Energy Projects",  # Using waste materials to generate renewable energy and reduce landfill waste, contributing to cleaner air.
    "Bioremediation with Plants",  # Using plants to clean up contaminated sites, improving soil and air quality.
    "Urban Farming",  # Introducing farming techniques in urban areas to reduce food miles, improve air quality, and strengthen local food systems.
    "Sustainable Forestry",  # Promoting responsible forestry practices to balance timber production and environmental conservation.
    "Environmental Education Programs",  # Educating communities about sustainability, air quality management, and environmental conservation.
    "Rainwater Harvesting",  # Collecting and using rainwater to reduce pressure on local water sources and ecosystems.
    "Biodiversity Conservation",  # Preserving biodiversity in urban and semi-urban areas to support ecosystems and wildlife.
    "Green Energy Solutions",  # Transitioning to renewable energy sources to reduce emissions and support long-term environmental health.
    "Community-Based Conservation",  # Engaging communities in managing natural resources sustainably, focusing on areas with moderate environmental conditions.
    "Pollution-Free Urban Development",  # Fostering urban growth with green buildings, clean energy, and low-emission transport solutions.
    "Climate-Smart Agriculture",  # Promoting agricultural practices that adapt to climate change while enhancing productivity and sustainability.
    "Carbon Sequestration",  # Implementing projects that increase carbon capture, including soil health improvements and forest expansion.
    "Recycling and Waste Reduction Programs",  # Encouraging recycling and waste management initiatives to reduce landfill impact and pollution.
]
green_infra_costs = {
    "Reforestation": 5.0,  # Cost in billion idr for reforestation efforts.
    "Urban Greening": 3.5,  # Cost for creating green urban spaces.
    "Agroforestry": 4.2,  # Cost for integrating trees with agriculture.
    "Green Infrastructure": 6.5,  # Cost for green infrastructure such as green roofs and sustainable urban water systems.
    "Air Quality Monitoring": 2.0,  # Cost for setting up monitoring stations and systems.
    "Community Tree Planting": 1.5,  # Cost for local community-driven tree planting initiatives.
    "Eco-friendly Public Transport Systems": 15.0,  # Cost for transitioning to low-emission public transport.
    "Pollution-Absorbing Green Walls": 3.8,  # Cost for installing green walls in cities.
    "Bioremediation with Plants": 2.5,  # Cost for using plants to remediate contaminated sites.
    "Green Energy Solutions": 20.0,  # Cost for implementing renewable energy systems like solar or wind.
    "Permeable Pavements and Green Streets": 4.0,  # Cost for designing cities with permeable pavements.
    "Wetlands Restoration": 6.0,  # Cost for restoring wetlands.
    "Pollution-Controlled Urban Parks": 5.5,  # Cost for designing parks that reduce air pollution.
    "Sustainable Agriculture Practices": 3.5,  # Cost for introducing sustainable farming techniques.
    "Windbreaks and Shelters": 2.2,  # Cost for planting windbreaks in rural or agricultural areas.
    "Environmental Education for Pollution Control": 1.0,  # Cost for community education programs.
    "Recycling and Waste Reduction Programs": 1.8,  # Cost for waste management and recycling initiatives.
    "Eco-Tourism": 7.0,  # Cost for promoting sustainable tourism.
    "Biodiversity Conservation": 8.0,  # Cost for conserving biodiversity.
    "Sustainable Agriculture Practices": 3.5,  # Cost for organic or permaculture techniques.
    "Forest Conservation": 6.0,  # Cost for conserving existing forests.
    "Wildlife Habitat Restoration": 4.0,  # Cost for restoring wildlife habitats.
    "Green Energy Projects": 20.0,  # Cost for renewable energy projects.
    "Pollution-Free Urban Development": 10.0,  # Cost for creating pollution-free urban environments.
    "Water Conservation and Management": 4.5,  # Cost for projects improving water conservation.
    "Carbon Sequestration": 5.5,  # Cost for carbon capture and forest expansion.
    "Rainwater Harvesting": 2.0,  # Cost for setting up rainwater collection systems.
    "Ecosystem-based Adaptation Projects": 5.0,  # Cost for utilizing ecosystems to adapt to climate change.
    "Conservation Agriculture": 3.0,  # Cost for promoting sustainable farming practices.
    "Urban Farming and Local Food Systems": 4.5,  # Cost for local food production in urban areas.
    "Agroecology": 3.2,  # Cost for applying ecological principles to agriculture.
    "Sustainable Forestry": 6.0,  # Cost for implementing responsible forestry practices.
    "Green Infrastructure in Cities": 8.0,  # Cost for creating green spaces and urban forests.
    "Rewilding Projects": 7.5,  # Cost for reintroducing species and restoring ecosystems.
    "Climate-Smart Agriculture": 3.8,  # Cost for promoting climate-resilient agricultural practices.
    "Community-Based Conservation": 4.0,  # Cost for involving communities in natural resource management.
    "Solar Home Systems": 1.5,  # Cost for small-scale solar systems for households.
    "Community Solar Power Projects": 3.5,  # Cost for shared solar projects.
    "Solar-Powered Water Pumps": 2.0,  # Cost for solar-powered water pumps in rural areas.
    "Micro-Hydropower Systems": 4.5,  # Cost for small-scale hydropower systems.
    "Biogas for Cooking": 2.2,  # Cost for providing biogas for cooking in off-grid areas.
    "Solar-Powered Lanterns": 1.0,  # Cost for providing solar-powered lighting.
    "Wind Turbine Microgrids": 6.5,  # Cost for small wind turbine-powered microgrids.
    "Clean Cookstoves Program": 1.8,  # Cost for distributing efficient cookstoves.
    "Rural Electrification with Solar": 8.0,  # Cost for solar-powered mini-grids or off-grid systems.
    "Water-Purification with Solar Power": 3.5,  # Cost for solar-powered water purification.
    "Community-Based Renewable Energy Cooperatives": 5.0,  # Cost for local cooperatives managing renewable energy projects.
    "Low-Cost Solar Panels and Financing": 2.5,  # Cost for affordable solar panels with micro-financing options.
    "Solar-Powered Refrigeration for Farmers": 3.0,  # Cost for solar-powered refrigeration in rural areas.
    "Energy Efficiency in Housing": 6.0,  # Cost for retrofitting homes with energy-efficient technologies.
    "Waste-to-Energy for Local Communities": 4.5,  # Cost for turning local waste into energy.
    "Solar-Powered Agricultural Irrigation": 3.5,  # Cost for solar-powered irrigation systems.
    "Community-Owned Wind Energy Projects": 5.5,  # Cost for community-owned wind energy projects.
    "Solar-Powered School and Health Clinics": 3.0,  # Cost for providing solar power to schools and clinics in off-grid areas.
    "Portable Solar Generators for Emergency Relief": 2.0,  # Cost for portable solar generators in emergencies.
    "Solar Power Farms": 10.0,  # Cost for large-scale solar installations.
    "Wind Energy Projects": 15.0,  # Cost for developing wind farms.
    "Geothermal Energy Development": 12.0,  # Cost for geothermal energy projects.
    "Hydropower Projects": 18.0,  # Cost for hydropower installations.
    "Community Solar Systems": 4.5,  # Cost for community-based solar systems.
    "Offshore Wind Farms": 20.0,  # Cost for offshore wind energy projects.
    "Electric Vehicle Charging Infrastructure": 7.5,  # Cost for building charging stations for electric vehicles.
    "Smart Grids for Clean Energy Integration": 5.0,  # Cost for upgrading power grids.
    "Energy Storage Systems (Batteries)": 8.0,  # Cost for large-scale energy storage systems.
    "Green Hydrogen Production": 12.0,  # Cost for producing hydrogen fuel using renewables.
    "Solar-Powered Desalination": 6.5,  # Cost for solar-powered desalination systems.
    "Biomass Power Generation": 7.0,  # Cost for biomass power plants.
    "Floating Solar Panels on Reservoirs": 8.0,  # Cost for installing floating solar panels.
    "Waste-to-Energy Facilities": 9.0,  # Cost for waste-to-energy plants.
    "Carbon Capture and Storage with Renewables": 10.0,  # Cost for combining renewable energy with carbon capture.
    "Energy-Efficient Smart Buildings": 9.0,  # Cost for building energy-efficient, renewable-powered smart buildings.
    "Microgrids with Renewable Energy": 7.5,  # Cost for small-scale renewable-powered grids.
    "Electric Grid Modernization for Renewable Integration": 10.0,  # Cost for modernizing the electric grid.
    "Renewable-Powered Data Centers": 12.0,  # Cost for creating renewable-powered data centers.
    "Sustainable Agriculture Practices": 3.5,  # Cost for implementing organic or sustainable farming methods.
    "Eco-friendly Public Transport Systems": 15.0,  # Cost for implementing low-emission public transportation.
    "Pollution-Controlled Urban Parks": 4.5,  # Cost for building urban parks that reduce pollution.
    "Water Conservation and Management": 4.5,  # Cost for improving water conservation in communities.
    "Agroforestry": 4.2,  # Cost for implementing agroforestry practices.
    "Green Infrastructure": 6.5,  # Cost for creating green infrastructure such as green roofs and urban trees.
    "Community Tree Planting": 1.5,  # Cost for community tree planting programs.
    "Waste-to-Energy Projects": 5.0,  # Cost for waste-to-energy conversion projects.
    "Bioremediation with Plants": 2.5,  # Cost for using plants to clean up contaminated sites.
    "Urban Farming": 4.0,  # Cost for developing urban farming systems.
    "Sustainable Forestry": 6.0,  # Cost for sustainable forestry practices.
    "Environmental Education Programs": 1.0,  # Cost for education programs to promote environmental awareness.
    "Rainwater Harvesting": 2.0,  # Cost for rainwater collection and storage systems.
    "Biodiversity Conservation": 8.0,  # Cost for conserving biodiversity.
    "Green Energy Solutions": 20.0,  # Cost for renewable energy solutions.
    "Community-Based Conservation": 4.0,  # Cost for community-driven conservation projects.
    "Pollution-Free Urban Development": 10.0,  # Cost for developing pollution-free urban areas.
    "Climate-Smart Agriculture": 3.8,  # Cost for promoting climate-smart agriculture practices.
    "Carbon Sequestration": 5.5,  # Cost for projects focused on carbon capture.
    "Recycling and Waste Reduction Programs": 2.0,  # Cost for waste reduction programs.
}
