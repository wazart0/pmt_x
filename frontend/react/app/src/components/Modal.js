import './modal.css'


const Modal = ({ handleClose, show, children }) => {
    const showHideClassName = show ? "modal display-block" : "modal display-none"

    return (
        <div className={showHideClassName}>
            <section className="modal-main">
                {children.content}
                <button type="button" onClick={handleClose}>Close</button>
            </section>
        </div>
    )
}


export default Modal
