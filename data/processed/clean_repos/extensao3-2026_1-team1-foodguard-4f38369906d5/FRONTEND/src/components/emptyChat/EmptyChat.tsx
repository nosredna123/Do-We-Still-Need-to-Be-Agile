import logo from "@/assets/logo.svg";

const EmptyChat = () => {
    return (
        <div className="flex flex-1 flex-col items-center justify-center gap-6 px-6">
            <img
                src={logo}
                alt="Logotipo FoodGuard"
                className="h-60 w-60 rounded-full shadow-md"
            />
            <h2 className="font-sansita text-5xl font-bold text-black">
                Inteligência que nutre
            </h2>
        </div>
    );
};

export default EmptyChat;
