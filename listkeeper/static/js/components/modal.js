export default {
  name: 'Modal',
  template: `
    <div class="modal" @keyup.esc="$emit('close')">
        <div class="container">
            <h3>
                <slot name="header-text"></slot>
                <a href="#" @click="$emit('close')" class="close"><i class="fa fa-times" aria-hidden="true"></i></a>
            </h3>
            <div class="content">
                <slot name="content"></slot>
            </div>
        </div>
    </div>
  `,
};
