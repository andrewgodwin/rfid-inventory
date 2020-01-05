export default {
  name: 'Modal',
  template: `
    <div class="modal" @keyup.esc="$emit('close')">
        <div class="container">
            <a href="#" @click="$emit('close')" class="close"><i class="fa fa-times" aria-hidden="true"></i></a>
            <slot name="content"></slot>
        </div>
    </div>
  `,
};
