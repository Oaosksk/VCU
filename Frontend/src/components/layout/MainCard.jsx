const MainCard = ({ children }) => {
    return (
        <div className="w-full max-w-4xl mx-auto px-4">
            <div className="card p-8 md:p-12 animate-fade-in">
                {children}
            </div>
        </div>
    )
}

export default MainCard
